<script setup lang="ts">
import { MenubarSubTrigger, type MenubarSubTriggerProps } from 'radix-vue'
import { ChevronRightIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<MenubarSubTriggerProps & { class?: string; inset?: boolean }>()
</script>

<template>
  <MenubarSubTrigger
    v-bind="props"
    data-slot="menubar-sub-trigger"
    :data-inset="inset"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-none select-none data-[inset]:pl-8',
      props.class
    )"
  >
    <slot />
    <ChevronRightIcon class="ml-auto h-4 w-4" />
  </MenubarSubTrigger>
</template>
