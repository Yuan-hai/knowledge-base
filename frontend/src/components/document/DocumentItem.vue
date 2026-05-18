<script setup lang="ts">
import type { DocumentInfo } from '../../types'

defineProps<{
  document: DocumentInfo
  selected: boolean
  ragMode: boolean
  deleting: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-select', id: string): void
  (e: 'delete', id: string): void
}>()

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <div
    class="group flex items-start gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-stone-100/70"
  >
    <label
      v-if="ragMode"
      class="mt-0.5 flex-shrink-0 cursor-pointer"
      @click.stop="emit('toggle-select', document.id)"
    >
      <div
        class="flex h-4 w-4 items-center justify-center rounded border transition-colors"
        :class="
          selected
            ? 'border-stone-700 bg-stone-700'
            : 'border-stone-300 bg-white hover:border-stone-400'
        "
      >
        <svg
          v-if="selected"
          class="h-3 w-3 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </label>

    <div
      class="min-w-0 flex-1 cursor-pointer"
      @click="ragMode && emit('toggle-select', document.id)"
    >
      <p class="truncate text-sm font-medium text-stone-700">
        {{ document.filename }}
      </p>
      <div class="mt-0.5 flex items-center gap-2 text-xs text-stone-400">
        <span>{{ formatDate(document.created_at) }}</span>
        <span class="text-stone-300">&middot;</span>
        <span>{{ document.chunk_count }} chunks</span>
      </div>
    </div>

    <button
      class="flex-shrink-0 rounded p-1 text-stone-300 opacity-0 transition-all hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
      :class="{ 'opacity-0': deleting }"
      :disabled="deleting"
      title="Delete document"
      @click.stop="emit('delete', document.id)"
    >
      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
        />
      </svg>
    </button>
  </div>
</template>
