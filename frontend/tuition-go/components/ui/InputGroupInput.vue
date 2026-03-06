<script setup lang="ts">
import { Input } from './input.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <Input
    v-bind="$attrs"
    data-slot="input-group-control"
    :class="cn(
      'flex-1 rounded-none border-0 bg-transparent shadow-none focus-visible:ring-0 dark:bg-transparent',
      props.class
    )"
  />
</template>
