<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  disabled: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'send', content: string): void
}>()

const text = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function handleSend() {
  const trimmed = text.value.trim()
  if (!trimmed) return
  emit('send', trimmed)
  text.value = ''
  adjustHeight()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function adjustHeight() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}
</script>

<template>
  <div class="border-t border-stone-100 bg-white px-4 py-3">
    <div class="flex items-end gap-2 rounded-xl border border-stone-200 bg-stone-50 px-3 py-2 transition-colors focus-within:border-stone-300 focus-within:bg-white focus-within:ring-1 focus-within:ring-stone-200">
      <textarea
        ref="textareaRef"
        v-model="text"
        :disabled="disabled"
        :placeholder="placeholder || $t('chat.placeholder')"
        rows="1"
        class="max-h-40 flex-1 resize-none bg-transparent text-sm text-stone-700 placeholder-stone-300 outline-none disabled:opacity-50"
        @keydown="onKeydown"
        @input="adjustHeight"
      />
      <button
        :disabled="disabled || !text.trim()"
        class="flex-shrink-0 rounded-lg p-1.5 text-stone-400 transition-colors hover:bg-stone-200 hover:text-stone-600 disabled:opacity-30 disabled:cursor-not-allowed"
        @click="handleSend"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 12h16m0 0l-6-6m6 6l-6 6"
          />
        </svg>
      </button>
    </div>
    <p class="mt-1.5 text-[10px] text-stone-300 text-center">
      {{ $t('chat.hint') }}
    </p>
  </div>
</template>
