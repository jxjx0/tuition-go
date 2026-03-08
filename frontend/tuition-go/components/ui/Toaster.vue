<script setup lang="ts">
import Toast from './Toast.vue'
import ToastClose from './ToastClose.vue'
import ToastDescription from './ToastDescription.vue'
import ToastProvider from './ToastProvider.vue'
import ToastTitle from './ToastTitle.vue'
import ToastViewport from './ToastViewport.vue'
import { useToast } from '@/hooks/use-toast'

const { toasts } = useToast()
</script>

<template>
  <ToastProvider>
    <Toast
      v-for="{ id, title, description, action, ...props } in toasts"
      :key="id"
      v-bind="props"
    >
      <div class="grid gap-1">
        <ToastTitle v-if="title">
          {{ title }}
        </ToastTitle>
        <ToastDescription v-if="description">
          {{ description }}
        </ToastDescription>
      </div>
      <template v-if="action">
        {{ action }}
      </template>
      <ToastClose />
    </Toast>
    <ToastViewport />
  </ToastProvider>
</template>
