<script setup lang="ts">
import { DrawerDescription, type DrawerDescriptionProps } from 'vaul-vue'
import { cn } from '@/lib/utils'

const props = defineProps<DrawerDescriptionProps & { class?: string }>()
</script>

<template>
  <DrawerDescription
    v-bind="props"
    :class="cn('text-muted-foreground text-sm', props.class)"
  >
    <slot />
  </DrawerDescription>
</template>
