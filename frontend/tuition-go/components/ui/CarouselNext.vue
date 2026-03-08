<script setup lang="ts">
import { inject } from 'vue'
import { ArrowRight } from 'lucide-vue-next'
import { Button } from './button.vue'
import { cn } from '@/lib/utils'

const context = inject<any>('carousel-context')

const props = withDefaults(defineProps<{
  variant?: 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  class?: string
}>(), {
  variant: 'outline',
  size: 'icon',
})
</script>

<template>
  <Button
    data-slot="carousel-next"
    :variant="variant"
    :size="size"
    :class="cn(
      'absolute size-8 rounded-full',
      context.orientation === 'horizontal'
        ? 'top-1/2 -right-12 -translate-y-1/2'
        : '-bottom-12 left-1/2 -translate-x-1/2 rotate-90',
      props.class
    )"
    :disabled="!context.canScrollNext.value"
    @click="context.scrollNext"
  >
    <ArrowRight class="size-4" />
    <span class="sr-only">Next slide</span>
  </Button>
</template>
