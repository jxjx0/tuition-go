<script setup lang="ts">
import { MinusIcon } from 'lucide-vue-next'

const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <div
    data-slot="input-otp-separator"
    role="separator"
    :class="props.class"
  >
    <MinusIcon />
  </div>
</template>
