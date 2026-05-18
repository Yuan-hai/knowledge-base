<script setup lang="ts">
import DocumentUpload from '../document/DocumentUpload.vue'
import DocumentList from '../document/DocumentList.vue'
import type { DocumentInfo } from '../../types'

defineProps<{
  documents: DocumentInfo[]
  documentsLoading: boolean
  uploading: boolean
  uploadProgress: number
  ragMode: boolean
  selectedDocIds: Set<string>
  deletingId: string | null
  uploadFolder: string
}>()

const emit = defineEmits<{
  (e: 'upload', file: File): void
  (e: 'toggle-select', id: string): void
  (e: 'delete', id: string): void
}>()
</script>

<template>
  <aside class="flex flex-col h-full w-[280px] border-r border-stone-100 bg-white flex-shrink-0">
    <DocumentUpload
      :uploading="uploading"
      :progress="uploadProgress"
      @upload="emit('upload', $event)"
    />

    <DocumentList
      :documents="documents"
      :loading="documentsLoading"
      :rag-mode="ragMode"
      :selected-doc-ids="selectedDocIds"
      :deleting-id="deletingId"
      @toggle-select="emit('toggle-select', $event)"
      @delete="emit('delete', $event)"
    />

    <div
      v-if="uploadFolder"
      class="border-t border-stone-50 px-3 py-2"
    >
      <p class="truncate text-[10px] text-stone-300">
        <span class="font-medium">Folder:</span> {{ uploadFolder }}
      </p>
    </div>
  </aside>
</template>
