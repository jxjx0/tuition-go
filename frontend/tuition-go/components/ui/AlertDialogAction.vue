<script setup lang="ts">
import { AlertDialogAction, type AlertDialogActionProps } from 'radix-vue'
import { buttonVariants } from './button.vue'
import { cn } from '@/lib/utils'

const props = defineProps<AlertDialogActionProps & { class?: string }>()
</script>

<template>
  <AlertDialogAction
    v-bind="props"
    :class="cn(buttonVariants(), props.class)"
  >
    <slot />
  </AlertDialogAction>
</template>
