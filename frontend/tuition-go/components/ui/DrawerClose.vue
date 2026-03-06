<script setup lang="ts">
import { DrawerClose, type DrawerCloseProps } from 'vaul-vue'

const props = defineProps<DrawerCloseProps>()
</script>

<template>
  <DrawerClose v-bind="props">
    <slot />
  </DrawerClose>
</template>
