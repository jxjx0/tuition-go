<script setup lang="ts">
import { ComboboxGroup, type ComboboxGroupProps, ComboboxLabel } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxGroupProps & { class?: string; heading?: string }>()
</script>

<template>
  <ComboboxGroup
    v-bind="props"
    data-slot="command-group"
    :class="cn(
      'text-foreground overflow-hidden p-1 [&_[data-slot=command-group-label]]:text-muted-foreground [&_[data-slot=command-group-label]]:px-2 [&_[data-slot=command-group-label]]:py-1.5 [&_[data-slot=command-group-label]]:text-xs [&_[data-slot=command-group-label]]:font-medium',
      props.class
    )"
  >
    <ComboboxLabel
      v-if="heading"
      data-slot="command-group-label"
    >
      {{ heading }}
    </ComboboxLabel>
    <slot />
  </ComboboxGroup>
</template>
