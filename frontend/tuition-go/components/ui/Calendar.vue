<script setup lang="ts">
import { computed } from 'vue'
import { Calendar as VCalendar } from 'v-calendar'
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { buttonVariants } from './button.vue'

const props = withDefaults(defineProps<{
  class?: string
  showOutsideDays?: boolean
}>(), {
  showOutsideDays: true,
})

const attributes = computed(() => [
  {
    key: 'today',
    highlight: {
      color: 'gray',
      fillMode: 'outline',
      class: '!bg-accent !text-accent-foreground',
    },
    dates: new Date(),
  },
])
</script>

<template>
  <VCalendar
    v-bind="$attrs"
    :attributes="attributes"
    :class="cn('p-3', props.class)"
    class="shadcn-calendar"
  >
    <template #header-left-button>
      <ChevronLeftIcon class="size-4" />
    </template>
    <template #header-right-button>
      <ChevronRightIcon class="size-4" />
    </template>
  </VCalendar>
</template>

<style>
.shadcn-calendar {
  --vc-font-family: inherit;
  --vc-rounded: var(--radius);
  --vc-font-size: 0.875rem;
  --vc-font-weight: 500;
  --vc-text-color: hsl(var(--foreground));
  --vc-bg: hsl(var(--background));
  --vc-border: hsl(var(--border));
  
  border: none !important;
  background: transparent !important;
}

.shadcn-calendar .vc-header {
  margin-bottom: 1rem;
}

.shadcn-calendar .vc-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.shadcn-calendar .vc-arrow {
  background: transparent;
  border: 1px solid hsl(var(--input));
  border-radius: var(--radius);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: colors 0.2s;
}

.shadcn-calendar .vc-arrow:hover {
  background: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}

.shadcn-calendar .vc-weekday {
  color: hsl(var(--muted-foreground));
  font-weight: 400;
  font-size: 0.8rem;
}

.shadcn-calendar .vc-day-content {
  width: 2rem;
  height: 2rem;
  font-size: 0.875rem;
  font-weight: 400;
  border-radius: var(--radius);
  transition: background-color 0.2s;
}

.shadcn-calendar .vc-day-content:hover {
  background-color: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}

.shadcn-calendar .vc-highlight {
  background-color: hsl(var(--primary)) !important;
  color: hsl(var(--primary-foreground)) !important;
}

.shadcn-calendar .vc-day.is-not-in-month * {
  opacity: 0.5;
}
</style>
