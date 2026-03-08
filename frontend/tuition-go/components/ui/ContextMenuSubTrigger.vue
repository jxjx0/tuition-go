<script setup lang="ts">
import { ContextMenuSubTrigger, type ContextMenuSubTriggerProps } from 'radix-vue'
import { ChevronRightIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<ContextMenuSubTriggerProps & { class?: string; inset?: boolean }>()
</script>

<template>
  <ContextMenuSubTrigger
    v-bind="props"
    data-slot="context-menu-sub-trigger"
    :data-inset="inset"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[inset]:pl-8 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class
    )"
  >
    <slot />
    <ChevronRightIcon class="ml-auto" />
  </ContextMenuSubTrigger>
</template>
