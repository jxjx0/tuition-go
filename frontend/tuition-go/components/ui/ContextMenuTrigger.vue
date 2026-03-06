<script setup lang="ts">
import { ContextMenuTrigger, type ContextMenuTriggerProps } from 'radix-vue'

const props = defineProps<ContextMenuTriggerProps>()
</script>

<template>
  <ContextMenuTrigger v-bind="props" data-slot="context-menu-trigger">
    <slot />
  </ContextMenuTrigger>
</template>
