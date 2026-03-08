<script setup lang="ts">
import { ComboboxSeparator, type ComboboxSeparatorProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxSeparatorProps & { class?: string }>()
</script>

<template>
  <ComboboxSeparator
    v-bind="props"
    data-slot="command-separator"
    :class="cn('bg-border -mx-1 h-px', props.class)"
  />
</template>
