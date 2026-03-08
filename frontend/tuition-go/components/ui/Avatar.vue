<script setup lang="ts">
import { AvatarRoot, type AvatarRootProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<AvatarRootProps & { class?: string }>()
</script>

<template>
  <AvatarRoot
    v-bind="props"
    data-slot="avatar"
    :class="cn(
      'relative flex size-8 shrink-0 overflow-hidden rounded-full',
      props.class
    )"
  >
    <slot />
  </AvatarRoot>
</template>
