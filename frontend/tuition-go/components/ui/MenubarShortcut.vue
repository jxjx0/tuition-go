<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <span
    data-slot="menubar-shortcut"
    :class="cn(
      'text-muted-foreground ml-auto text-xs tracking-widest',
      props.class
    )"
  >
    <slot />
  </span>
</template>
