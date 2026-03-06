<script setup lang="ts">
import { Textarea } from './textarea.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <Textarea
    v-bind="$attrs"
    data-slot="input-group-control"
    :class="cn(
      'flex-1 resize-none rounded-none border-0 bg-transparent py-3 shadow-none focus-visible:ring-0 dark:bg-transparent',
      props.class
    )"
  />
</template>
