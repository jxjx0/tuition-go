<script setup lang="ts">
import { Primitive } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  as?: string
  asChild?: boolean
  class?: string
}>()
</script>

<template>
  <Primitive
    :as="as || 'div'"
    :as-child="asChild"
    :class="cn(
      'bg-muted flex items-center gap-2 rounded-md border px-4 text-sm font-medium shadow-xs [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4',
      props.class
    )"
  >
    <slot />
  </Primitive>
</template>
