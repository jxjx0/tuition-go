<script setup lang="ts">
import { inject } from 'vue'
import { PanelLeftIcon } from 'lucide-vue-next'
import { Button } from './button.vue'
import { cn } from '@/lib/utils'

const context = inject<any>('sidebar-context')

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <Button
    data-sidebar="trigger"
    data-slot="sidebar-trigger"
    variant="ghost"
    size="icon"
    :class="cn('size-7', props.class)"
    @click="context.toggleSidebar"
  >
    <PanelLeftIcon class="size-4" />
    <span class="sr-only">Toggle Sidebar</span>
  </Button>
</template>
