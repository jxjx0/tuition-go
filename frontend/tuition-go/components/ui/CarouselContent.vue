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
    :ref="context.emblaRef"
    class="overflow-hidden"
    data-slot="carousel-content"
  >
    <div
      :class="cn(
        'flex',
        context.orientation === 'horizontal' ? '-ml-4' : '-mt-4 flex-col',
        props.class
      )"
    >
      <slot />
    </div>
  </div>
</template>
