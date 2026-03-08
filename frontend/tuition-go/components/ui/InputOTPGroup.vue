<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <div
    data-slot="input-otp-group"
    :class="cn('flex items-center', props.class)"
  >
    <slot />
  </div>
</template>
