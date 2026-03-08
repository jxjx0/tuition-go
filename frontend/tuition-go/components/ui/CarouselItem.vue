<script setup lang="ts">
import { inject } from 'vue'
import { cn } from '@/lib/utils'

const context = inject<any>('carousel-context')

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <div
    role="group"
    aria-roledescription="slide"
    data-slot="carousel-item"
    :class="cn(
      'min-w-0 shrink-0 grow-0 basis-full',
      context.orientation === 'horizontal' ? 'pl-4' : 'pt-4',
      props.class
    )"
  >
    <slot />
  </div>
</template>
