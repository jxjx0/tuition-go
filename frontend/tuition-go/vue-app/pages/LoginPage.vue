<script setup lang="ts">
import { SignIn, } from '@clerk/vue'
</script>




<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16" style="background:linear-gradient(135deg,#F5F7FA 0%,#E8F0FE 100%)">
    <SignIn signUpFallbackRedirectUrl="/dashboard" />
  </div>
</template>
