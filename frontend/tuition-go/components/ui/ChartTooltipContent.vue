<script setup lang="ts">
import { inject } from 'vue'
import { cn } from '@/lib/utils'

const config = inject<any>('chart-config')

const props = defineProps<{
  active?: boolean
  payload?: any[]
  label?: string
  class?: string
}>()
</script>

<template>
  <div
    v-if="active && payload?.length"
    :class="cn(
      'border-border/50 bg-background grid min-w-[8rem] items-start gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs shadow-xl',
      props.class
    )"
  >
    <div class="font-medium">{{ label }}</div>
    <div class="grid gap-1.5">
      <div
        v-for="(item, index) in payload"
        :key="index"
        class="flex items-center gap-2"
      >
        <div
          class="size-2 rounded-[2px]"
          :style="{ backgroundColor: item.color || (config && config[item.name]?.color) }"
        />
        <div class="flex flex-1 justify-between leading-none">
          <span class="text-muted-foreground">
            {{ (config && config[item.name]?.label) || item.name }}
          </span>
          <span class="text-foreground font-mono font-medium tabular-nums">
            {{ item.value.toLocaleString() }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
