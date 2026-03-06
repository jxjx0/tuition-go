<script setup lang="ts">
import { TooltipRoot, type TooltipRootEmits, type TooltipRootProps, useForwardPropsEmits } from 'radix-vue'
import TooltipProvider from './TooltipProvider.vue'

const props = defineProps<TooltipRootProps>()
const emits = defineEmits<TooltipRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <TooltipProvider>
    <TooltipRoot v-bind="forwarded">
      <slot />
    </TooltipRoot>
  </TooltipProvider>
</template>
