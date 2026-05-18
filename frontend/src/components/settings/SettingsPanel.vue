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
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: { selectedModel: string; uploadFolder: string }): void
}>()

const localModel = ref(props.selectedModel)
const localFolder = ref(props.uploadFolder)

watch(
  () => [props.selectedModel, props.uploadFolder],
  () => {
    localModel.value = props.selectedModel
    localFolder.value = props.uploadFolder
  }
)

function handleSave() {
  emit('save', {
    selectedModel: localModel.value,
    uploadFolder: localFolder.value,
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
              <h2 class="text-base font-medium text-stone-800">Settings</h2>
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
                  Upload Folder
                </label>
                <input
                  v-model="localFolder"
                  type="text"
                  placeholder="/path/to/documents"
                  class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-700 shadow-sm transition-colors placeholder:text-stone-300 focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
                />
                <p class="text-xs text-stone-400">
                  Absolute path to the folder for document uploads.
                </p>
              </div>
            </div>

            <div class="border-t border-stone-100 px-5 py-4">
              <button
                :disabled="saving"
                class="w-full rounded-lg bg-stone-800 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-stone-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                @click="handleSave"
              >
                <LoadingSpinner v-if="saving" size="sm" />
                <span>{{ saving ? 'Saving...' : 'Save Settings' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
