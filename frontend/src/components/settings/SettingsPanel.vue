<script setup lang="ts">
import { ref, watch } from 'vue'
import ModelSelector from './ModelSelector.vue'
import LoadingSpinner from '../shared/LoadingSpinner.vue'
import type { ModelInfo } from '../../types'

const props = defineProps<{
  visible: boolean
  selectedModel: string
  uploadFolder: string
  availableModels: ModelInfo[]
  saving: boolean
  apiKey: string
  apiBaseUrl: string
  apiEmbeddingUrl: string
  embeddingModel: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: {
    selectedModel: string
    uploadFolder: string
    apiKey: string
    apiBaseUrl: string
    apiEmbeddingUrl: string
    embeddingModel: string
  }): void
}>()

const localModel = ref(props.selectedModel)
const localFolder = ref(props.uploadFolder)
const localApiKey = ref(props.apiKey)
const localApiBaseUrl = ref(props.apiBaseUrl)
const localApiEmbeddingUrl = ref(props.apiEmbeddingUrl)
const localEmbeddingModel = ref(props.embeddingModel)
const showApiKey = ref(false)

watch(
  () => [props.selectedModel, props.uploadFolder, props.apiKey, props.apiBaseUrl, props.apiEmbeddingUrl, props.embeddingModel],
  () => {
    localModel.value = props.selectedModel
    localFolder.value = props.uploadFolder
    localApiKey.value = props.apiKey
    localApiBaseUrl.value = props.apiBaseUrl
    localApiEmbeddingUrl.value = props.apiEmbeddingUrl
    localEmbeddingModel.value = props.embeddingModel
  }
)

function handleSave() {
  emit('save', {
    selectedModel: localModel.value,
    uploadFolder: localFolder.value,
    apiKey: localApiKey.value,
    apiBaseUrl: localApiBaseUrl.value,
    apiEmbeddingUrl: localApiEmbeddingUrl.value,
    embeddingModel: localEmbeddingModel.value,
  })
}
</script>

<template>
  <Teleport to="body">
    <div>
      <Transition
        enter-active-class="transition-opacity duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="visible"
          class="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
          @click="emit('close')"
        />
      </Transition>

      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div
          v-if="visible"
          class="fixed right-0 top-0 z-50 h-full w-80 bg-white shadow-2xl border-l border-stone-100"
        >
          <div class="flex flex-col h-full">
            <div class="flex items-center justify-between border-b border-stone-100 px-5 py-4">
              <h2 class="text-base font-medium text-stone-800">{{ $t('settings.title') }}</h2>
              <button
                class="rounded-lg p-1.5 text-stone-400 hover:bg-stone-50 hover:text-stone-600 transition-colors"
                @click="emit('close')"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="flex-1 overflow-y-auto p-5 space-y-6">
              <ModelSelector
                :models="availableModels"
                :model-value="localModel"
                @update:model-value="localModel = $event"
              />

              <div class="space-y-2">
                <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
                  {{ $t('settings.uploadFolder') }}
                </label>
                <input
                  v-model="localFolder"
                  type="text"
                  placeholder="/path/to/documents"
                  class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                />
                <p class="text-xs text-stone-400">
                  {{ $t('settings.uploadFolderDesc') }}
                </p>
              </div>

              <!-- Divider -->
              <div class="border-t border-stone-100" />

              <div class="space-y-2">
                <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
                  {{ $t('settings.apiKey') }}
                </label>
                <div class="relative">
                  <input
                    v-model="localApiKey"
                    :type="showApiKey ? 'text' : 'password'"
                    :placeholder="$t('settings.apiKeyPlaceholder')"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 pr-9 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                  />
                  <button
                    type="button"
                    class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600 transition-colors"
                    @click="showApiKey = !showApiKey"
                    :title="showApiKey ? $t('settings.hide') : $t('settings.show')"
                  >
                    <!-- Eye icon when hidden (show password) -->
                    <svg v-if="!showApiKey" class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <!-- Eye-off icon when visible (hide password) -->
                    <svg v-else class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
                  {{ $t('settings.apiBaseUrl') }}
                </label>
                <div class="relative">
                  <input
                    v-model="localApiBaseUrl"
                    type="text"
                    list="chat-url-list"
                    :placeholder="$t('settings.apiBaseUrlPlaceholder')"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 pr-8 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                  />
                  <svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                <datalist id="chat-url-list">
                  <option value="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions">
                    阿里百炼 (DashScope)
                  </option>
                  <option value="https://api.deepseek.com/v1/chat/completions">
                    DeepSeek
                  </option>
                  <option value="https://api.openai.com/v1/chat/completions">
                    OpenAI
                  </option>
                </datalist>
              </div>

              <div class="space-y-2">
                <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
                  {{ $t('settings.apiEmbeddingUrl') }}
                </label>
                <div class="relative">
                  <input
                    v-model="localApiEmbeddingUrl"
                    type="text"
                    list="embed-url-list"
                    :placeholder="$t('settings.apiEmbeddingUrlPlaceholder')"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 pr-8 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                  />
                  <svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                <datalist id="embed-url-list">
                  <option value="https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding">
                    阿里百炼 (DashScope)
                  </option>
                  <option value="https://api.deepseek.com/v1/embeddings">
                    DeepSeek
                  </option>
                  <option value="https://api.openai.com/v1/embeddings">
                    OpenAI
                  </option>
                </datalist>
              </div>

              <div class="space-y-2">
                <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
                  {{ $t('settings.embeddingModel') }}
                </label>
                <input
                  v-model="localEmbeddingModel"
                  type="text"
                  :placeholder="$t('settings.embeddingModelPlaceholder')"
                  class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                />
              </div>
            </div>

            <div class="border-t border-stone-100 px-5 py-4">
              <button
                :disabled="saving"
                class="w-full rounded-lg bg-stone-800 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-stone-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                @click="handleSave"
              >
                <LoadingSpinner v-if="saving" size="sm" />
                <span>{{ saving ? $t('settings.saving') : $t('settings.save') }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
