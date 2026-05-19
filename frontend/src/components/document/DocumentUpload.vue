<script setup lang="ts">
import { ref } from 'vue'
import LoadingSpinner from '../shared/LoadingSpinner.vue'

const props = defineProps<{
  uploading: boolean
  progress: number
}>()

const emit = defineEmits<{
  (e: 'upload', file: File): void
}>()

const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onDragOver(e: DragEvent) {
  e.preventDefault()
  dragging.value = true
}

function onDragLeave() {
  dragging.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) handleFile(file)
  target.value = ''
}

function handleFile(file: File) {
  const allowed = ['.pdf', '.docx', '.txt', '.md']
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!allowed.includes(ext)) {
    return
  }
  emit('upload', file)
}
</script>

<template>
  <div class="px-3 pt-3 pb-2">
    <div
      class="relative rounded-lg border-2 border-dashed transition-colors cursor-pointer"
      :class="
        dragging
          ? 'border-stone-400 bg-stone-100/50'
          : 'border-stone-200 hover:border-stone-300 hover:bg-stone-50/50'
      "
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
      @click="fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx,.txt,.md"
        class="hidden"
        @change="onFileChange"
      />

      <div v-if="uploading" class="flex flex-col items-center px-4 py-4">
        <LoadingSpinner size="sm" />
        <p class="mt-2 text-xs text-stone-500">{{ $t('documents.uploading') }} {{ progress }}%</p>
        <div class="mt-2 h-1 w-full overflow-hidden rounded-full bg-stone-100">
          <div
            class="h-full rounded-full bg-stone-600 transition-all duration-300"
            :style="{ width: progress + '%' }"
          />
        </div>
      </div>

      <div v-else class="flex flex-col items-center px-4 py-4">
        <svg
          class="h-6 w-6 text-stone-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <p class="mt-1 text-xs text-stone-400">
          {{ $t('documents.uploadHint') }}
        </p>
        <p class="mt-0.5 text-[10px] text-stone-300">{{ $t('documents.uploadFormats') }}</p>
      </div>
    </div>
  </div>
</template>
