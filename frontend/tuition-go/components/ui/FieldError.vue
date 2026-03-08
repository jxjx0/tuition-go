<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  errors?: Array<{ message?: string } | undefined> | string | string[]
  class?: string
}>()

const errorMessages = computed(() => {
  if (typeof props.errors === 'string') return [props.errors]
  if (Array.isArray(props.errors)) {
    return props.errors.map(e => typeof e === 'string' ? e : e?.message).filter(Boolean)
  }
  return []
})
</script>

<template>
  <div
    v-if="errorMessages.length"
    role="alert"
    data-slot="field-error"
    :class="cn('text-destructive text-sm font-normal', props.class)"
  >
    <template v-if="errorMessages.length === 1">
      {{ errorMessages[0] }}
    </template>
    <ul v-else class="ml-4 flex list-disc flex-col gap-1">
      <li v-for="(msg, i) in errorMessages" :key="i">
        {{ msg }}
      </li>
    </ul>
  </div>
</template>
