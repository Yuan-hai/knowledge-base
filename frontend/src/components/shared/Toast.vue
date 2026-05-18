<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps<{
  message: string
  type?: 'success' | 'error' | 'info'
  visible: boolean
  duration?: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const show = ref(false)
let timerId: ReturnType<typeof setTimeout> | null = null

watch(
  () => props.visible,
  (val) => {
    if (val) {
      show.value = true
      if (props.duration !== 0) {
        if (timerId) clearTimeout(timerId)
        timerId = setTimeout(() => {
          show.value = false
          emit('close')
          timerId = null
        }, props.duration || 3000)
      }
    } else {
      show.value = false
      if (timerId) {
        clearTimeout(timerId)
        timerId = null
      }
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (timerId) {
    clearTimeout(timerId)
    timerId = null
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="show"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-lg px-5 py-3 text-sm shadow-lg backdrop-blur-sm"
        :class="{
          'bg-emerald-50 text-emerald-800 border border-emerald-200': type === 'success',
          'bg-red-50 text-red-800 border border-red-200': type === 'error',
          'bg-stone-50 text-stone-700 border border-stone-200': type === 'info' || !type,
        }"
      >
        <svg
          v-if="type === 'success'"
          class="h-4 w-4 text-emerald-500 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg
          v-if="type === 'error'"
          class="h-4 w-4 text-red-500 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span>{{ message }}</span>
        <button
          class="ml-2 flex-shrink-0 rounded p-0.5 hover:bg-black/5 transition-colors"
          @click="show = false; emit('close')"
        >
          <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>
