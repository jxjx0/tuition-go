<script setup lang="ts">
import { ErrorMessage } from 'vee-validate'
import { inject } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: string
}>()

const name = inject<string>('form-field-name')
</script>

<template>
  <ErrorMessage
    v-if="name"
    :name="name"
    as="p"
    data-slot="form-message"
    :class="cn('text-destructive text-sm', props.class)"
  />
</template>
