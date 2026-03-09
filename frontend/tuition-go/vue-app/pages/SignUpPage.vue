<script setup lang="ts">
import { ref, computed } from 'vue'
import { SignUp, useAuth } from '@clerk/vue'

const { isSignedIn } = useAuth()
const selectedRole = ref<'student'|'tutor'>('student')
const redirectUrl = computed(() =>
  selectedRole.value === 'tutor' ? '/tutor-dashboard' : '/dashboard'
)
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16" style="background:linear-gradient(135deg,#F5F7FA 0%,#E8F0FE 100%)">
    <div class="w-full max-w-md">
      <!-- Role toggle -->
      <p class="text-sm font-medium mb-2 text-center" style="color:#1B3A5C">I want to sign up as a</p>
      <div class="flex rounded-xl overflow-hidden mb-4 border" style="border-color:#E8F0FE">
        <button @click="selectedRole='student'" :disabled="isSignedIn" class="flex-1 px-4 py-3 text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed" :style="selectedRole==='student'?'background-color:#4A90D9;color:#fff':'background-color:#fff;color:#1B3A5C'">
          Student
        </button>
        <button @click="selectedRole='tutor'" :disabled="isSignedIn" class="flex-1 px-4 py-3 text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed" :style="selectedRole==='tutor'?'background-color:#2EAA4F;color:#fff':'background-color:#fff;color:#1B3A5C'">
          Tutor
        </button>
      </div>

      <!-- Clerk SignUp -->
      <div class="flex justify-center">
        <SignUp :unsafeMetadata="{ role: selectedRole }" :forceRedirectUrl="redirectUrl" :signInFallbackRedirectUrl="redirectUrl" />
      </div>
    </div>
  </div>
</template>
