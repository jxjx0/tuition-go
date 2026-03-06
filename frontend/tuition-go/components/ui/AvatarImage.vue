<script setup lang="ts">
import { AvatarImage, type AvatarImageProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<AvatarImageProps & { class?: string }>()
</script>

<template>
  <AvatarImage
    v-bind="props"
    data-slot="avatar-image"
    :class="cn('aspect-square size-full', props.class)"
  />
</template>
