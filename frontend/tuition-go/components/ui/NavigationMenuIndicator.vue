<script setup lang="ts">
import { NavigationMenuIndicator, type NavigationMenuIndicatorProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<NavigationMenuIndicatorProps & { class?: string }>()
</script>

<template>
  <NavigationMenuIndicator
    v-bind="props"
    data-slot="navigation-menu-indicator"
    :class="cn(
      'data-[state=visible]:animate-in data-[state=hidden]:animate-out data-[state=hidden]:fade-out data-[state=visible]:fade-in top-full z-[1] flex h-1.5 items-end justify-center overflow-hidden',
      props.class
    )"
  >
    <div class="bg-border relative top-[60%] h-2 w-2 rotate-45 rounded-tl-sm shadow-md" />
  </NavigationMenuIndicator>
</template>
