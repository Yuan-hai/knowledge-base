<script setup lang="ts">
import { ref } from 'vue'
import type { ChatMessage as ChatMessageType } from '../../types'

defineProps<{
  message: ChatMessageType
  sources?: string[]
}>()

const sourcesExpanded = ref(false)
</script>

<template>
  <div
    class="flex w-full"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
      :class="
        message.role === 'user'
          ? 'bg-stone-800 text-white'
          : 'bg-stone-50 text-stone-700 border border-stone-100'
      "
    >
      <div class="whitespace-pre-wrap break-words">{{ message.content }}</div>

      <div v-if="sources && sources.length > 0" class="mt-2 border-t border-stone-200 pt-2">
        <button
          class="flex items-center gap-1 text-xs font-medium text-stone-400 hover:text-stone-600 transition-colors"
          @click="sourcesExpanded = !sourcesExpanded"
        >
          <svg
            class="h-3 w-3 transition-transform"
            :class="{ 'rotate-90': sourcesExpanded }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          {{ sources.length }} {{ sources.length > 1 ? $t('chat.sources') : $t('chat.source') }}
        </button>
        <div
          v-if="sourcesExpanded"
          class="mt-2 space-y-1 pl-1"
        >
          <div
            v-for="(source, idx) in sources"
            :key="idx"
            class="rounded-md bg-white/60 px-2.5 py-1.5 text-xs text-stone-500 border border-stone-100"
          >
            <span class="font-medium text-stone-600">{{ idx + 1 }}.</span> {{ source }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
