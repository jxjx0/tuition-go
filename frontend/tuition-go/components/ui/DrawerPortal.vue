<script setup lang="ts">
import { DrawerPortal, type DrawerPortalProps } from 'vaul-vue'

const props = defineProps<DrawerPortalProps>()
</script>

<template>
  <DrawerPortal v-bind="props">
    <slot />
  </DrawerPortal>
</template>
