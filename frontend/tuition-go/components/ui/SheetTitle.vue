<script setup lang="ts">
import { DialogTitle, type DialogTitleProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<DialogTitleProps & { class?: string }>()
</script>

<template>
  <DialogTitle
    v-bind="props"
    data-slot="sheet-title"
    :class="cn('text-foreground font-semibold', props.class)"
  >
    <slot />
  </DialogTitle>
</template>
