<script setup lang="ts">
import { AlertDialogDescription, type AlertDialogDescriptionProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<AlertDialogDescriptionProps & { class?: string }>()
</script>

<template>
  <AlertDialogDescription
    v-bind="props"
    :class="cn('text-muted-foreground text-sm', props.class)"
  >
    <slot />
  </AlertDialogDescription>
</template>
