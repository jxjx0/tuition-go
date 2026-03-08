<script setup lang="ts">
import { inject } from 'vue'
import { Slot } from 'radix-vue'

const formItemId = inject<string>('form-item-id')
</script>

<template>
  <Slot
    data-slot="form-control"
    :id="formItemId"
  >
    <slot />
  </Slot>
</template>
