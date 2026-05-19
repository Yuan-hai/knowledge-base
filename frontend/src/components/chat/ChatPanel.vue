<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import type { ChatMessage as ChatMessageType } from '../../types'

const props = defineProps<{
  messages: ChatMessageType[]
  streaming: boolean
  messageSources?: Record<number, string[]>
}>()

const emit = defineEmits<{
  (e: 'send', content: string): void
}>()

const messagesContainer = ref<HTMLDivElement | null>(null)

function scrollToBottom() {
  nextTick(() => {
    const el = messagesContainer.value
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => {
  const last = props.messages[props.messages.length - 1]
  return last?.content
}, scrollToBottom)

onMounted(scrollToBottom)
</script>

<template>
  <div class="flex flex-col flex-1 min-h-0">
    <!-- Messages area -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-6 space-y-4"
    >
      <div
        v-if="messages.length === 0"
        class="flex flex-col items-center justify-center h-full text-center"
      >
        <div class="rounded-2xl bg-stone-50 p-8 max-w-sm">
          <svg
            class="mx-auto h-10 w-10 text-stone-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <h3 class="mt-4 text-base font-medium text-stone-500">
            {{ $t('chat.assistant') }}
          </h3>
          <p class="mt-2 text-sm text-stone-400 leading-relaxed">
            {{ $t('chat.prompt') }}
          </p>
        </div>
      </div>

      <ChatMessage
        v-for="(msg, idx) in messages"
        :key="idx"
        :message="msg"
        :sources="messageSources?.[idx]"
      />

      <div
        v-if="streaming && messages.length > 0 && messages[messages.length - 1].role === 'assistant'"
        class="flex items-center gap-1 px-4 text-stone-400"
      >
        <span class="flex gap-1">
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-400" style="animation-delay: 0ms" />
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-400" style="animation-delay: 150ms" />
          <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-stone-400" style="animation-delay: 300ms" />
        </span>
      </div>
    </div>

    <!-- Input area -->
    <ChatInput
      :disabled="streaming"
      @send="emit('send', $event)"
    />
  </div>
</template>
