<script setup lang="ts">
import { ToastDescription, type ToastDescriptionProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ToastDescriptionProps & { class?: string }>()
</script>

<template>
  <ToastDescription
    v-bind="props"
    :class="cn('text-sm opacity-90', props.class)"
  >
    <slot />
  </ToastDescription>
</template>
