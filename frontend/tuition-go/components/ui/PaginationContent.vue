<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <ul
    data-slot="pagination-content"
    :class="cn('flex flex-row items-center gap-1', props.class)"
  >
    <slot />
  </ul>
</template>
