<script setup lang="ts">
import { PinInputRoot, type PinInputRootEmits, type PinInputRootProps, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<PinInputRootProps & { class?: string }>()
const emits = defineEmits<PinInputRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <PinInputRoot
    v-bind="forwarded"
    data-slot="input-otp"
    :class="cn('flex items-center gap-2 has-disabled:opacity-50', props.class)"
  >
    <slot />
  </PinInputRoot>
</template>
