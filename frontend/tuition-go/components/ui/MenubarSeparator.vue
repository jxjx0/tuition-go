<script setup lang="ts">
import { MenubarSeparator, type MenubarSeparatorProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<MenubarSeparatorProps & { class?: string }>()
</script>

<template>
  <MenubarSeparator
    v-bind="props"
    data-slot="menubar-separator"
    :class="cn('bg-border -mx-1 my-1 h-px', props.class)"
  />
</template>
