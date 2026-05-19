import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import type { DocumentInfo } from '../types'

export function useDocuments() {
  const { t } = useI18n()
  const documents = ref<DocumentInfo[]>([])
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref<string | null>(null)

  async function fetchDocuments() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<DocumentInfo[]>('/documents')
      documents.value = data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || t('messages.loadDocsFailed')
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(file: File) {
    uploading.value = true
    uploadProgress.value = 0
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post<DocumentInfo>('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) {
            uploadProgress.value = Math.round((e.loaded * 100) / e.total)
          }
        },
      })
      documents.value.push(data)
      return data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || t('messages.uploadFailed')
      return null
    } finally {
      uploading.value = false
      uploadProgress.value = 0
    }
  }

  async function deleteDocument(id: string) {
    error.value = null
    try {
      await api.delete(`/documents/${id}`)
      documents.value = documents.value.filter((d) => d.id !== id)
      return true
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || t('messages.deleteFailed')
      return false
    }
  }

  return {
    documents,
    loading,
    uploading,
    uploadProgress,
    error,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
  }
}
