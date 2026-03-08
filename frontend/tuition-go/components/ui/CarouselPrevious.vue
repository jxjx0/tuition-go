<script setup lang="ts">
import { inject } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
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
    data-slot="carousel-previous"
    :variant="variant"
    :size="size"
    :class="cn(
      'absolute size-8 rounded-full',
      context.orientation === 'horizontal'
        ? 'top-1/2 -left-12 -translate-y-1/2'
        : '-top-12 left-1/2 -translate-x-1/2 rotate-90',
      props.class
    )"
    :disabled="!context.canScrollPrev.value"
    @click="context.scrollPrev"
  >
    <ArrowLeft class="size-4" />
    <span class="sr-only">Previous slide</span>
  </Button>
</template>
