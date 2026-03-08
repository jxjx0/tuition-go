<script setup lang="ts">
import { DrawerTrigger, type DrawerTriggerProps } from 'vaul-vue'

const props = defineProps<DrawerTriggerProps>()
</script>

<template>
  <DrawerTrigger v-bind="props">
    <slot />
  </DrawerTrigger>
</template>
