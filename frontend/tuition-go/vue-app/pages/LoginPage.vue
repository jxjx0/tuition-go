<script setup lang="ts">
import { SignInButton } from '@clerk/vue'
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16" style="background:linear-gradient(135deg,#F5F7FA 0%,#E8F0FE 100%)">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-xl border p-8" style="border-color:#E8F0FE">
        <div class="text-center mb-8">
          <div class="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4" style="background:linear-gradient(135deg,#4A90D9,#1B3A5C)">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold" style="color:#1B3A5C">Welcome back</h1>
          <p class="text-sm mt-2" style="color:#1B3A5C;opacity:0.6">Sign in to continue your learning journey</p>
        </div>
        <SignInButton
          mode="modal"
          fallback-redirect-url="/#/dashboard"
        >
          <button class="w-full px-4 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90" style="background-color:#4A90D9">
            Sign In
          </button>
        </SignInButton>
        <p class="text-center text-sm mt-6" style="color:#1B3A5C;opacity:0.6">
          Don't have an account? <router-link to="/signup" class="font-semibold hover:underline" style="color:#4A90D9">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
