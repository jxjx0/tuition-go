<script setup lang="ts">
import { DrawerTitle, type DrawerTitleProps } from 'vaul-vue'
import { cn } from '@/lib/utils'

const props = defineProps<DrawerTitleProps & { class?: string }>()
</script>

<template>
  <DrawerTitle
    v-bind="props"
    :class="cn('text-lg font-semibold leading-none tracking-tight', props.class)"
  >
    <slot />
  </DrawerTitle>
</template>
