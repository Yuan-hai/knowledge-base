<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  modelName: string
}>()

const emit = defineEmits<{
  (e: 'open-settings'): void
}>()

const { locale } = useI18n()

function toggleLocale() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}
</script>

<template>
  <header class="flex items-center justify-between border-b border-stone-100 bg-white px-5 py-3">
    <div class="flex items-center gap-3">
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-stone-800">
        <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      </div>
      <h1 class="text-base font-semibold tracking-tight text-stone-800">{{ $t('app.title') }}</h1>
    </div>

    <div class="flex items-center gap-3">
      <div
        v-if="modelName"
        class="hidden sm:flex items-center gap-1.5 rounded-full bg-stone-50 px-3 py-1.5 text-xs text-stone-500 border border-stone-100"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-400" />
        {{ modelName }}
      </div>

      <button
        class="rounded-lg px-2 py-1 text-xs font-medium text-stone-400 hover:bg-stone-50 hover:text-stone-600 transition-colors"
        @click="toggleLocale"
      >
        {{ locale === 'zh' ? 'EN' : '中' }}
      </button>

      <button
        class="rounded-lg p-1.5 text-stone-300 hover:bg-stone-50 hover:text-stone-500 transition-colors"
        :title="$t('app.settings')"
        @click="emit('open-settings')"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>
    </div>
  </header>
</template>
