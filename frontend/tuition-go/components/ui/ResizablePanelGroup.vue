<script setup lang="ts">
import { PanelGroup, type PanelGroupProps } from 'vue-resizable-panels'
import { cn } from '@/lib/utils'

const props = defineProps<PanelGroupProps & { class?: string }>()
</script>

<template>
  <PanelGroup
    v-bind="props"
    data-slot="resizable-panel-group"
    :class="cn(
      'flex h-full w-full data-[panel-group-direction=vertical]:flex-col',
      props.class
    )"
  >
    <slot />
  </PanelGroup>
</template>
