<script setup lang="ts">
import { ChevronLeftIcon } from 'lucide-vue-next'
import PaginationLink from './PaginationLink.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <PaginationLink
    aria-label="Go to previous page"
    size="default"
    :class="cn('gap-1 px-2.5 sm:pl-2.5', props.class)"
  >
    <ChevronLeftIcon class="size-4" />
    <span class="hidden sm:block">Previous</span>
  </PaginationLink>
</template>
