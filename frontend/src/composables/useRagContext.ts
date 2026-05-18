import { ref, computed } from 'vue'

export function useRagContext() {
  const selectedDocIds = ref<Set<string>>(new Set())

  const selectedCount = computed(() => selectedDocIds.value.size)

  function toggleDocument(id: string) {
    const next = new Set(selectedDocIds.value)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    selectedDocIds.value = next
  }

  function isSelected(id: string): boolean {
    return selectedDocIds.value.has(id)
  }

  function clearSelection() {
    selectedDocIds.value = new Set()
  }

  function getSelectedIds(): string[] {
    return Array.from(selectedDocIds.value)
  }

  return {
    selectedDocIds,
    selectedCount,
    toggleDocument,
    isSelected,
    clearSelection,
    getSelectedIds,
  }
}
