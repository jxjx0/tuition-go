<script setup lang="ts">
import { DrawerOverlay, type DrawerOverlayProps } from 'vaul-vue'
import { cn } from '@/lib/utils'

const props = defineProps<DrawerOverlayProps & { class?: string }>()
</script>

<template>
  <DrawerOverlay
    v-bind="props"
    :class="cn('bg-black/80 fixed inset-0 z-50', props.class)"
  />
</template>
