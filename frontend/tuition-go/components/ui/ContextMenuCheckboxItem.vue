<script setup lang="ts">
import { ContextMenuCheckboxItem, type ContextMenuCheckboxItemEmits, type ContextMenuCheckboxItemProps, ContextMenuItemIndicator, useForwardPropsEmits } from 'radix-vue'
import { CheckIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<ContextMenuCheckboxItemProps & { class?: string }>()
const emits = defineEmits<ContextMenuCheckboxItemEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <ContextMenuCheckboxItem
    v-bind="forwarded"
    data-slot="context-menu-checkbox-item"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground relative flex cursor-default items-center gap-2 rounded-sm py-1.5 pr-2 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class
    )"
  >
    <span class="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
      <ContextMenuItemIndicator>
        <CheckIcon class="size-4" />
      </ContextMenuItemIndicator>
    </span>
    <slot />
  </ContextMenuCheckboxItem>
</template>
