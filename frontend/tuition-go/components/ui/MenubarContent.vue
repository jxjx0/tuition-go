<script setup lang="ts">
import { MenubarContent, type MenubarContentEmits, type MenubarContentProps, MenubarPortal, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<MenubarContentProps & { class?: string }>(), {
  align: 'start',
  alignOffset: -4,
  sideOffset: 8,
})
const emits = defineEmits<MenubarContentEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <MenubarPortal>
    <MenubarContent
      v-bind="forwarded"
      data-slot="menubar-content"
      :class="cn(
        'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 min-w-[12rem] origin-(--radix-menubar-content-transform-origin) overflow-hidden rounded-md border p-1 shadow-md',
        props.class
      )"
    >
      <slot />
    </MenubarContent>
  </MenubarPortal>
</template>
