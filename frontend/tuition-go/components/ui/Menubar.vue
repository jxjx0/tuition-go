<script setup lang="ts">
import { MenubarRoot, type MenubarRootEmits, type MenubarRootProps, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<MenubarRootProps & { class?: string }>()
const emits = defineEmits<MenubarRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <MenubarRoot
    v-bind="forwarded"
    data-slot="menubar"
    :class="cn(
      'bg-background flex h-9 items-center gap-1 rounded-md border p-1 shadow-xs',
      props.class
    )"
  >
    <slot />
  </MenubarRoot>
</template>
