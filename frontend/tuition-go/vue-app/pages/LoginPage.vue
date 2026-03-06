<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function demoLogin(role: string) { 
  router.push(role === 'student' ? '/dashboard' : '/tutor-dashboard') 
}
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
        <div class="rounded-xl p-6 mb-6 text-center" style="background-color:#F5F7FA;border:2px dashed #E8F0FE">
          <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" style="background-color:#E8F0FE">
            <svg class="w-6 h-6" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <p class="text-sm font-semibold mb-1" style="color:#1B3A5C">Clerk Authentication</p>
          <p class="text-xs" style="color:#1B3A5C;opacity:0.6">&lt;SignIn /&gt; component renders here</p>
          <p class="text-xs mt-2" style="color:#4A90D9">Supports Google, GitHub, and email login</p>
        </div>
        <div class="space-y-3">
          <button @click="demoLogin('student')" class="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90" style="background-color:#4A90D9">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            Continue as Student (Demo)
          </button>
          <button @click="demoLogin('tutor')" class="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90" style="background-color:#1B3A5C">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0H5"/>
            </svg>
            Continue as Tutor (Demo)
          </button>
        </div>
        <p class="text-center text-sm mt-6" style="color:#1B3A5C;opacity:0.6">
          Don't have an account? <router-link to="/signup" class="font-semibold hover:underline" style="color:#4A90D9">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
