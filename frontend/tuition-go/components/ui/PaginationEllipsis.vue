<script setup lang="ts">
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <span
    aria-hidden
    data-slot="pagination-ellipsis"
    :class="cn('flex size-9 items-center justify-center', props.class)"
  >
    <MoreHorizontalIcon class="size-4" />
    <span class="sr-only">More pages</span>
  </span>
</template>
