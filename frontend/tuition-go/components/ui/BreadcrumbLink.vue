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
    :as="as || 'a'"
    :as-child="asChild"
    data-slot="breadcrumb-link"
    :class="cn('hover:text-foreground transition-colors', props.class)"
  >
    <slot />
  </Primitive>
</template>
