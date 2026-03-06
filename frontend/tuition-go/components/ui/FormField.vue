<script setup lang="ts">
import { useId } from 'vue'
import { Field as VeeField } from 'vee-validate'
import { provide } from 'vue'

const props = defineProps<{
  name: string
}>()

const id = useId()
provide('form-field-id', id)
provide('form-field-name', props.name)
</script>

<template>
  <VeeField :name="name" v-bind="$attrs" v-slot="{ field, errorMessage, meta }">
    <slot :field="field" :error-message="errorMessage" :meta="meta" />
  </VeeField>
</template>
