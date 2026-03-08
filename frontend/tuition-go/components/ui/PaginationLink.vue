<script setup lang="ts">
import { Primitive } from 'radix-vue'
import { buttonVariants } from './button.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  as?: string
  asChild?: boolean
  isActive?: boolean
  size?: 'default' | 'sm' | 'lg' | 'icon'
  class?: string
}>(), {
  size: 'icon',
})
</script>

<template>
  <Primitive
    :as="as || 'a'"
    :as-child="asChild"
    :aria-current="isActive ? 'page' : undefined"
    data-slot="pagination-link"
    :data-active="isActive"
    :class="cn(
      buttonVariants({
        variant: isActive ? 'outline' : 'ghost',
        size,
      }),
      props.class
    )"
  >
    <slot />
  </Primitive>
</template>
