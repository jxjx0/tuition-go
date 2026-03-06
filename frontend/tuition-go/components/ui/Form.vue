<script setup lang="ts">
import { Form as VeeForm } from 'vee-validate'

// Alias Form to VeeForm for Shadcn compatibility
export const Form = VeeForm
</script>

<template>
  <VeeForm v-bind="$attrs">
    <slot v-bind="slotProps" v-for="(slotProps, name) in $slots" :name="name" />
  </VeeForm>
</template>
