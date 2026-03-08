<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <div
    data-slot="empty-content"
    :class="cn(
      'flex w-full max-w-sm min-w-0 flex-col items-center gap-4 text-sm text-balance',
      props.class
    )"
  >
    <slot />
  </div>
</template>
