<script setup lang="ts">
import { Panel, type PanelProps } from 'vue-resizable-panels'

const props = defineProps<PanelProps>()
</script>

<template>
  <Panel v-bind="props" data-slot="resizable-panel">
    <slot />
  </Panel>
</template>
