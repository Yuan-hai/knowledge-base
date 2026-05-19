<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/layout/AppHeader.vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import ChatPanel from '../components/chat/ChatPanel.vue'
import ChatModeToggle from '../components/chat/ChatModeToggle.vue'
import SettingsPanel from '../components/settings/SettingsPanel.vue'
import Toast from '../components/shared/Toast.vue'
import { useSettings } from '../composables/useSettings'
import { useDocuments } from '../composables/useDocuments'
import { useRagContext } from '../composables/useRagContext'
import { useChat } from '../composables/useChat'

const { t } = useI18n()

const {
  selectedModel,
  uploadFolder,
  availableModels,
  apiKey,
  apiBaseUrl,
  apiEmbeddingUrl,
  embeddingModel,
  saving: settingsSaving,
  fetchSettings,
  updateSettings,
} = useSettings()

const {
  documents,
  loading: docsLoading,
  uploading,
  uploadProgress,
  fetchDocuments,
  uploadDocument,
  deleteDocument,
} = useDocuments()

const {
  selectedDocIds,
  selectedCount,
  toggleDocument,
} = useRagContext()

const {
  messages,
  streaming,
  currentModel,
  messageSources,
  sendChatMessage,
  sendRagQuery,
} = useChat()

const mode = ref<'chat' | 'rag'>('chat')
const settingsVisible = ref(false)
const deletingId = ref<string | null>(null)

const toast = ref({
  visible: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'info',
})

function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
  toast.value = { visible: true, message, type }
}

function onCloseToast() {
  toast.value.visible = false
}

async function handleSendMessage(content: string) {
  currentModel.value = selectedModel.value

  if (mode.value === 'rag') {
    const docIds = Array.from(selectedDocIds.value)
    if (docIds.length === 0) {
      showToast(t('chat.needSelect'), 'info')
      return
    }
    await sendRagQuery(content, docIds, selectedModel.value)
  } else {
    await sendChatMessage(content, selectedModel.value)
  }
}

async function handleUpload(file: File) {
  const result = await uploadDocument(file)
  if (result) {
    showToast(`"${result.filename}" ${t('messages.uploadSuccess')}`, 'success')
  }
}

async function handleDelete(id: string) {
  deletingId.value = id
  const success = await deleteDocument(id)
  deletingId.value = null
  if (success) {
    if (selectedDocIds.value.has(id)) {
      toggleDocument(id)
    }
    showToast(t('messages.docDeleted'), 'success')
  }
}

async function handleSaveSettings(data: {
  selectedModel: string
  uploadFolder: string
  apiKey: string
  apiBaseUrl: string
  apiEmbeddingUrl: string
  embeddingModel: string
}) {
  selectedModel.value = data.selectedModel
  uploadFolder.value = data.uploadFolder
  apiKey.value = data.apiKey
  apiBaseUrl.value = data.apiBaseUrl
  apiEmbeddingUrl.value = data.apiEmbeddingUrl
  embeddingModel.value = data.embeddingModel
  const success = await updateSettings()
  if (success) {
    settingsVisible.value = false
    showToast(t('messages.settingsSaved'), 'success')
  }
}

onMounted(async () => {
  await fetchSettings()
  await fetchDocuments()
})
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-stone-50/50">
    <AppHeader
      :model-name="selectedModel"
      @open-settings="settingsVisible = true"
    />

    <div class="flex flex-1 overflow-hidden">
      <AppSidebar
        :documents="documents"
        :documents-loading="docsLoading"
        :uploading="uploading"
        :upload-progress="uploadProgress"
        :rag-mode="mode === 'rag'"
        :selected-doc-ids="selectedDocIds"
        :deleting-id="deletingId"
        :upload-folder="uploadFolder"
        @upload="handleUpload"
        @toggle-select="toggleDocument"
        @delete="handleDelete"
      />

      <main class="flex flex-col flex-1 min-w-0">
        <div class="flex items-center justify-between border-b border-stone-100 bg-white px-4 py-2">
          <ChatModeToggle
            :mode="mode"
            :selected-doc-count="selectedCount"
            @update:mode="mode = $event"
          />
          <p class="text-[10px] text-stone-300">
            {{ mode === 'rag' ? $t('chat.ragMode') : $t('chat.chatMode') }}
          </p>
        </div>

        <ChatPanel
          :messages="messages"
          :streaming="streaming"
          :message-sources="messageSources"
          @send="handleSendMessage"
        />
      </main>
    </div>

    <SettingsPanel
      :visible="settingsVisible"
      :selected-model="selectedModel"
      :upload-folder="uploadFolder"
      :available-models="availableModels"
      :saving="settingsSaving"
      :api-key="apiKey"
      :api-base-url="apiBaseUrl"
      :api-embedding-url="apiEmbeddingUrl"
      :embedding-model="embeddingModel"
      @close="settingsVisible = false"
      @save="handleSaveSettings"
    />

    <Toast
      :message="toast.message"
      :type="toast.type"
      :visible="toast.visible"
      @close="onCloseToast"
    />
  </div>
</template>
