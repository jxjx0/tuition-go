<script setup lang="ts">
import { AuthenticateWithRedirectCallback } from '@clerk/vue'
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center">
    <AuthenticateWithRedirectCallback
      sign-in-fallback-redirect-url="/#/dashboard"
      sign-up-fallback-redirect-url="/#/dashboard"
    />
  </div>
</template>
