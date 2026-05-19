<script setup lang="ts">
defineProps<{
  mode: 'chat' | 'rag'
  selectedDocCount: number
}>()

const emit = defineEmits<{
  (e: 'update:mode', value: 'chat' | 'rag'): void
}>()
</script>

<template>
  <div class="flex items-center gap-2">
    <div class="flex rounded-lg bg-stone-100 p-0.5">
      <button
        class="rounded-md px-3 py-1.5 text-xs font-medium transition-all"
        :class="
          mode === 'chat'
            ? 'bg-white text-stone-700 shadow-sm'
            : 'text-stone-400 hover:text-stone-500'
        "
        @click="emit('update:mode', 'chat')"
      >
        {{ $t('mode.chat') }}
      </button>
      <button
        class="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all"
        :class="
          mode === 'rag'
            ? 'bg-white text-stone-700 shadow-sm'
            : 'text-stone-400 hover:text-stone-500'
        "
        @click="emit('update:mode', 'rag')"
      >
        {{ $t('mode.rag') }}
        <span
          v-if="selectedDocCount > 0"
          class="inline-flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-stone-700 px-1 text-[10px] font-semibold text-white"
        >
          {{ selectedDocCount }}
        </span>
      </button>
    </div>
  </div>
</template>
