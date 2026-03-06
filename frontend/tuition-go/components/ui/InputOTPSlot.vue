<script setup lang="ts">
import { PinInputInput, type PinInputInputProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<PinInputInputProps & { class?: string }>()
</script>

<template>
  <PinInputInput
    v-bind="props"
    data-slot="input-otp-slot"
    :class="cn(
      'data-[active=true]:border-ring data-[active=true]:ring-ring/50 data-[active=true]:aria-invalid:ring-destructive/20 dark:data-[active=true]:aria-invalid:ring-destructive/40 aria-invalid:border-destructive data-[active=true]:aria-invalid:border-destructive dark:bg-input/30 border-input relative flex h-9 w-9 items-center justify-center border-y border-r text-sm shadow-xs transition-all outline-none first:rounded-l-md first:border-l last:rounded-r-md data-[active=true]:z-10 data-[active=true]:ring-[3px]',
      props.class
    )"
  />
</template>
