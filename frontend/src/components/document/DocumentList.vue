<script setup lang="ts">
import DocumentItem from './DocumentItem.vue'
import LoadingSpinner from '../shared/LoadingSpinner.vue'
import type { DocumentInfo } from '../../types'

defineProps<{
  documents: DocumentInfo[]
  loading: boolean
  ragMode: boolean
  selectedDocIds: Set<string>
  deletingId: string | null
}>()

const emit = defineEmits<{
  (e: 'toggle-select', id: string): void
  (e: 'delete', id: string): void
}>()
</script>

<template>
  <div class="flex-1 overflow-hidden flex flex-col min-h-0">
    <div class="flex items-center justify-between px-3 py-2">
      <span class="text-xs font-medium tracking-wide uppercase text-stone-400">
        {{ $t('documents.title') }}
        <span v-if="documents.length" class="ml-1 text-stone-300">({{ documents.length }})</span>
      </span>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <LoadingSpinner />
    </div>

    <div
      v-else-if="documents.length === 0"
      class="flex flex-col items-center justify-center py-10 px-4"
    >
      <svg class="h-8 w-8 text-stone-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <p class="mt-3 text-sm text-stone-400">{{ $t('documents.empty') }}</p>
      <p class="mt-1 text-xs text-stone-300">{{ $t('documents.emptyHint') }}</p>
    </div>

    <div v-else class="flex-1 overflow-y-auto space-y-0.5 px-2 pb-3">
      <DocumentItem
        v-for="doc in documents"
        :key="doc.id"
        :document="doc"
        :selected="selectedDocIds.has(doc.id)"
        :rag-mode="ragMode"
        :deleting="deletingId === doc.id"
        @toggle-select="emit('toggle-select', $event)"
        @delete="emit('delete', $event)"
      />
    </div>
  </div>
</template>
