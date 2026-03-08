<script setup lang="ts">
import { ContextMenuSeparator, type ContextMenuSeparatorProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ContextMenuSeparatorProps & { class?: string }>()
</script>

<template>
  <ContextMenuSeparator
    v-bind="props"
    data-slot="context-menu-separator"
    :class="cn('bg-border -mx-1 my-1 h-px', props.class)"
  />
</template>
