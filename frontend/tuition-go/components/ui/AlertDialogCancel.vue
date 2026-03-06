<script setup lang="ts">
import { AlertDialogCancel, type AlertDialogCancelProps } from 'radix-vue'
import { buttonVariants } from './button.vue'
import { cn } from '@/lib/utils'

const props = defineProps<AlertDialogCancelProps & { class?: string }>()
</script>

<template>
  <AlertDialogCancel
    v-bind="props"
    :class="cn(buttonVariants({ variant: 'outline' }), props.class)"
  >
    <slot />
  </AlertDialogCancel>
</template>
