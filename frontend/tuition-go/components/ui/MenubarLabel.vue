<script setup lang="ts">
import { MenubarLabel, type MenubarLabelProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<MenubarLabelProps & { class?: string; inset?: boolean }>()
</script>

<template>
  <MenubarLabel
    v-bind="props"
    data-slot="menubar-label"
    :data-inset="inset"
    :class="cn(
      'px-2 py-1.5 text-sm font-medium data-[inset]:pl-8',
      props.class
    )"
  >
    <slot />
  </MenubarLabel>
</template>
