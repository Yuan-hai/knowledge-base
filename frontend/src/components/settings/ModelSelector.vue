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
      {{ $t('settings.model') }}
    </label>
    <input
      type="text"
      list="model-list"
      :value="modelValue"
      :placeholder="$t('settings.selectModel')"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-700 shadow-sm transition-colors focus:border-stone-400 focus:outline-none focus:ring-1 focus:ring-stone-400"
    />
    <datalist id="model-list">
      <option
        v-for="model in models"
        :key="model.id"
        :value="model.id"
      >
        {{ model.name }}
      </option>
    </datalist>
  </div>
</template>
