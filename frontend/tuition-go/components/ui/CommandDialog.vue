<script setup lang="ts">
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './dialog'
import Command from './Command.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  open?: boolean
  title?: string
  description?: string
  showCloseButton?: boolean
  class?: string
}>(), {
  title: 'Command Palette',
  description: 'Search for a command to run...',
  showCloseButton: true,
})

const emits = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="open" @update:open="emits('update:open', $event)">
    <DialogHeader class="sr-only">
      <DialogTitle>{{ title }}</DialogTitle>
      <DialogDescription>{{ description }}</DialogDescription>
    </DialogHeader>
    <DialogContent
      :class="cn('overflow-hidden p-0', props.class)"
      :show-close-button="showCloseButton"
    >
      <Command class="[&_[data-slot=command-group-label]]:text-muted-foreground **:data-[slot=command-input-wrapper]:h-12 [&_[data-slot=command-group-label]]:px-2 [&_[data-slot=command-group-label]]:font-medium [&_[data-slot=command-group]]:px-2 [&_[data-slot=command-group]:not([hidden])_~[data-slot=command-group]]:pt-0 [&_[data-slot=command-input-wrapper]_svg]:h-5 [&_[data-slot=command-input-wrapper]_svg]:w-5 [&_[data-slot=command-input]]:h-12 [&_[data-slot=command-item]]:px-2 [&_[data-slot=command-item]]:py-3 [&_[data-slot=command-item]_svg]:h-5 [&_[data-slot=command-item]_svg]:w-5">
        <slot />
      </Command>
    </DialogContent>
  </Dialog>
</template>
