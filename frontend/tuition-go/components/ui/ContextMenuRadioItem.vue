<script setup lang="ts">
import { ContextMenuItemIndicator, ContextMenuRadioItem, type ContextMenuRadioItemEmits, type ContextMenuRadioItemProps, useForwardPropsEmits } from 'radix-vue'
import { CircleIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<ContextMenuRadioItemProps & { class?: string }>()
const emits = defineEmits<ContextMenuRadioItemEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <ContextMenuRadioItem
    v-bind="forwarded"
    data-slot="context-menu-radio-item"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground relative flex cursor-default items-center gap-2 rounded-sm py-1.5 pr-2 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class
    )"
  >
    <span class="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
      <ContextMenuItemIndicator>
        <CircleIcon class="size-2 fill-current" />
      </ContextMenuItemIndicator>
    </span>
    <slot />
  </ContextMenuRadioItem>
</template>
