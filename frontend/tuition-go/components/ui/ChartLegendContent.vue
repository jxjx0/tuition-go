<script setup lang="ts">
import { inject } from 'vue'
import { cn } from '@/lib/utils'

const config = inject<any>('chart-config')

const props = defineProps<{
  payload?: any[]
  verticalAlign?: 'top' | 'bottom'
  class?: string
}>()
</script>

<template>
  <div
    v-if="payload?.length"
    :class="cn(
      'flex items-center justify-center gap-4',
      verticalAlign === 'top' ? 'pb-3' : 'pt-3',
      props.class
    )"
  >
    <div
      v-for="(item, index) in payload"
      :key="index"
      class="flex items-center gap-1.5 [&>svg]:h-3 [&>svg]:w-3"
    >
      <div
        class="h-2 w-2 shrink-0 rounded-[2px]"
        :style="{ backgroundColor: item.color || (config && config[item.name]?.color) }"
      />
      <span>{{ (config && config[item.name]?.label) || item.name }}</span>
    </div>
  </div>
</template>
