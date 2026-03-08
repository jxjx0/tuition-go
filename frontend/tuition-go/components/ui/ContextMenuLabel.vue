<script setup lang="ts">
import { ContextMenuLabel, type ContextMenuLabelProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ContextMenuLabelProps & { class?: string; inset?: boolean }>()
</script>

<template>
  <ContextMenuLabel
    v-bind="props"
    data-slot="context-menu-label"
    :data-inset="inset"
    :class="cn(
      'text-foreground px-2 py-1.5 text-sm font-medium data-[inset]:pl-8',
      props.class
    )"
  >
    <slot />
  </ContextMenuLabel>
</template>
