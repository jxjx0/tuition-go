<script setup lang="ts">
import { SelectLabel, type SelectLabelProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<SelectLabelProps & { class?: string }>()
</script>

<template>
  <SelectLabel
    v-bind="props"
    data-slot="select-label"
    :class="cn('text-muted-foreground px-2 py-1.5 text-xs', props.class)"
  >
    <slot />
  </SelectLabel>
</template>
