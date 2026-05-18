import { ref } from 'vue'
import api from '../api'
import type { SettingsResponse, ModelInfo } from '../types'

export function useSettings() {
  const selectedModel = ref<string>('')
  const uploadFolder = ref<string>('')
  const availableModels = ref<ModelInfo[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)

  async function fetchSettings() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<SettingsResponse>('/settings')
      selectedModel.value = data.selected_model
      uploadFolder.value = data.upload_folder
      availableModels.value = data.available_models
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || 'Failed to load settings'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings() {
    saving.value = true
    error.value = null
    try {
      const { data } = await api.put<SettingsResponse>('/settings', {
        selected_model: selectedModel.value,
        upload_folder: uploadFolder.value,
      })
      selectedModel.value = data.selected_model
      uploadFolder.value = data.upload_folder
      availableModels.value = data.available_models
      return true
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || 'Failed to save settings'
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    selectedModel,
    uploadFolder,
    availableModels,
    loading,
    saving,
    error,
    fetchSettings,
    updateSettings,
  }
}
