<script setup lang="ts">
import { MenubarPortal, type MenubarPortalProps } from 'radix-vue'

const props = defineProps<MenubarPortalProps>()
</script>

<template>
  <MenubarPortal v-bind="props" data-slot="menubar-portal">
    <slot />
  </MenubarPortal>
</template>
