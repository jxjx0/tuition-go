<script setup lang="ts">
import { inject } from 'vue'
import { Label } from './label.vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()

const formItemId = inject<string>('form-item-id')
</script>

<template>
  <Label
    data-slot="form-label"
    :class="cn('data-[error=true]:text-destructive', props.class)"
    :for="formItemId"
  >
    <slot />
  </Label>
</template>
