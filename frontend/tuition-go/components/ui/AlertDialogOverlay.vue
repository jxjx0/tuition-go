<script setup lang="ts">
import { AlertDialogOverlay, type AlertDialogOverlayProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<AlertDialogOverlayProps & { class?: string }>()
</script>

<template>
  <AlertDialogOverlay
    v-bind="props"
    :class="cn(
      'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/50',
      props.class
    )"
  />
</template>
