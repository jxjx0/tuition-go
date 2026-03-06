<script setup lang="ts">
import { Input } from './input.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
  modelValue?: string
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<template>
  <Input
    data-slot="sidebar-input"
    data-sidebar="input"
    :class="cn('bg-background h-8 w-full shadow-none', props.class)"
    :model-value="modelValue"
    @update:model-value="emits('update:modelValue', $event)"
  />
</template>
