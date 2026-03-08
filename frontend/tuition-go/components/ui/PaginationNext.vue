<script setup lang="ts">
import { ChevronRightIcon } from 'lucide-vue-next'
import PaginationLink from './PaginationLink.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <PaginationLink
    aria-label="Go to next page"
    size="default"
    :class="cn('gap-1 px-2.5 sm:pr-2.5', props.class)"
  >
    <span class="hidden sm:block">Next</span>
    <ChevronRightIcon class="size-4" />
  </PaginationLink>
</template>
