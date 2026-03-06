<script setup lang="ts">
import { NavigationMenuItem, type NavigationMenuItemProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<NavigationMenuItemProps & { class?: string }>()
</script>

<template>
  <NavigationMenuItem
    v-bind="props"
    data-slot="navigation-menu-item"
    :class="cn('relative', props.class)"
  >
    <slot />
  </NavigationMenuItem>
</template>
