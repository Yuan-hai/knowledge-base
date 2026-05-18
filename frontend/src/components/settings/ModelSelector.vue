<script setup lang="ts">
import type { ModelInfo } from '../../types'

defineProps<{
  models: ModelInfo[]
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<template>
  <div class="space-y-2">
    <label class="block text-xs font-medium tracking-wide uppercase text-stone-400">
      AI Model
    </label>
    <select
      :value="modelValue"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-700 shadow-sm transition-colors focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
    >
      <option value="" disabled>Select a model...</option>
      <option
        v-for="model in models"
        :key="model.id"
        :value="model.id"
      >
        {{ model.name }}
      </option>
    </select>
  </div>
</template>
