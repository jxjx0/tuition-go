<script setup lang="ts">
import { AvatarFallback, type AvatarFallbackProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<AvatarFallbackProps & { class?: string }>()
</script>

<template>
  <AvatarFallback
    v-bind="props"
    data-slot="avatar-fallback"
    :class="cn(
      'bg-muted flex size-full items-center justify-center rounded-full',
      props.class
    )"
  >
    <slot />
  </AvatarFallback>
</template>
