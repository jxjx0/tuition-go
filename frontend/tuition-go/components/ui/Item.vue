<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { Primitive } from 'radix-vue'
import { cn } from '@/lib/utils'

const itemVariants = cva(
  'group/item flex items-center border border-transparent text-sm rounded-md transition-colors [a&]:hover:bg-accent/50 [a&]:transition-colors duration-100 flex-wrap outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
  {
    variants: {
      variant: {
        default: 'bg-transparent',
        outline: 'border-border',
        muted: 'bg-muted/50',
      },
      size: {
        default: 'p-4 gap-4 ',
        sm: 'py-3 px-4 gap-2.5',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const props = withDefaults(defineProps<{
  as?: string
  asChild?: boolean
  variant?: 'default' | 'outline' | 'muted'
  size?: 'default' | 'sm'
  class?: string
}>(), {
  variant: 'default',
  size: 'default',
})
</script>

<template>
  <Primitive
    :as="as || 'div'"
    :as-child="asChild"
    data-slot="item"
    :data-variant="variant"
    :data-size="size"
    :class="cn(itemVariants({ variant, size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
