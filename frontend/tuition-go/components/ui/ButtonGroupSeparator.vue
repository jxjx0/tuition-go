<script setup lang="ts">
import { Separator } from './separator.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  orientation?: 'horizontal' | 'vertical'
  class?: string
}>(), {
  orientation: 'vertical',
})
</script>

<template>
  <Separator
    data-slot="button-group-separator"
    :orientation="orientation"
    :class="cn(
      'bg-input relative !m-0 self-stretch data-[orientation=vertical]:h-auto',
      props.class
    )"
  />
</template>
