<script setup lang="ts">
import { ComboboxItem, type ComboboxItemEmits, type ComboboxItemProps, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxItemProps & { class?: string }>()
const emits = defineEmits<ComboboxItemEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <ComboboxItem
    v-bind="forwarded"
    data-slot="command-item"
    :class="cn(
      'data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class
    )"
  >
    <slot />
  </ComboboxItem>
</template>
