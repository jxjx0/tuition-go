<script setup lang="ts">
import { MenubarSub, type MenubarSubEmits, type MenubarSubProps, useForwardPropsEmits } from 'radix-vue'

const props = defineProps<MenubarSubProps>()
const emits = defineEmits<MenubarSubEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <MenubarSub v-bind="forwarded" data-slot="menubar-sub">
    <slot />
  </MenubarSub>
</template>
