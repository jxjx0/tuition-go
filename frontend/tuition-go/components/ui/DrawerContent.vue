<script setup lang="ts">
import { DrawerContent, type DrawerContentProps } from 'vaul-vue'
import DrawerPortal from './DrawerPortal.vue'
import DrawerOverlay from './DrawerOverlay.vue'
import { cn } from '@/lib/utils'

const props = defineProps<DrawerContentProps & { class?: string }>()
</script>

<template>
  <DrawerPortal>
    <DrawerOverlay />
    <DrawerContent
      v-bind="props"
      :class="cn(
        'bg-background border-border fixed inset-x-0 bottom-0 z-50 mt-24 flex h-auto flex-col rounded-t-[10px] border',
        props.class
      )"
    >
      <div class="bg-muted mx-auto mt-4 h-2 w-[100px] rounded-full" />
      <slot />
    </DrawerContent>
  </DrawerPortal>
</template>
