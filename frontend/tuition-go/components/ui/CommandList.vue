<script setup lang="ts">
import { ComboboxContent, type ComboboxContentProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxContentProps & { class?: string }>()
</script>

<template>
  <ComboboxContent
    v-bind="props"
    data-slot="command-list"
    :class="cn(
      'max-h-[300px] scroll-py-1 overflow-x-hidden overflow-y-auto',
      props.class
    )"
  >
    <slot />
  </ComboboxContent>
</template>
