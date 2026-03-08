<script setup lang="ts">
import { provide } from 'vue'
import { VisXYContainer, VisLine, VisArea, VisAxis, VisCrosshair, VisTooltip } from '@unovis/vue'
import { cn } from '@/lib/utils'

export type ChartConfig = {
  [k: string]: {
    label?: string
    color?: string
  }
}

const props = defineProps<{
  config: ChartConfig
  class?: string
}>()

provide('chart-config', props.config)
</script>

<template>
  <div
    data-slot="chart"
    :class="cn('flex aspect-video justify-center text-xs', props.class)"
  >
    <slot />
  </div>
</template>
