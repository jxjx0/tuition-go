<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { Button } from './button.vue'
import { cn } from '@/lib/utils'

const inputGroupButtonVariants = cva(
  'text-sm shadow-none flex gap-2 items-center',
  {
    variants: {
      size: {
        xs: "h-6 gap-1 px-2 rounded-[calc(var(--radius)-5px)] [&>svg:not([class*='size-'])]:size-3.5 has-[>svg]:px-2",
        sm: 'h-8 px-2.5 gap-1.5 rounded-md has-[>svg]:px-2.5',
        'icon-xs':
          'size-6 rounded-[calc(var(--radius)-5px)] p-0 has-[>svg]:p-0',
        'icon-sm': 'size-8 p-0 has-[>svg]:p-0',
      },
    },
    defaultVariants: {
      size: 'xs',
    },
  },
)

const props = withDefaults(defineProps<{
  variant?: string
  size?: 'xs' | 'sm' | 'icon-xs' | 'icon-sm'
  class?: string
}>(), {
  variant: 'ghost',
  size: 'xs',
})
</script>

<template>
  <Button
    v-bind="$attrs"
    :data-size="size"
    :variant="variant"
    :class="cn(inputGroupButtonVariants({ size }), props.class)"
  >
    <slot />
  </Button>
</template>
