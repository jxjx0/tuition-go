<script setup lang="ts">
import { ref } from 'vue'
import { SignUpButton } from '@clerk/vue'

const selectedRole = ref<'student'|'tutor'>('student')
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16" style="background:linear-gradient(135deg,#F5F7FA 0%,#E8F0FE 100%)">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-xl border p-8" style="border-color:#E8F0FE">
        <div class="text-center mb-8">
          <div class="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4" style="background:linear-gradient(135deg,#2EAA4F,#1B3A5C)">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold" style="color:#1B3A5C">Create your account</h1>
          <p class="text-sm mt-2" style="color:#1B3A5C;opacity:0.6">Join 5,000+ students on EduMatch</p>
        </div>
        <div class="mb-6">
          <p class="text-sm font-medium mb-3" style="color:#1B3A5C">I want to join as a:</p>
          <div class="grid grid-cols-2 gap-3">
            <button @click="selectedRole='student'" class="p-4 rounded-xl border-2 text-center transition-all" :style="selectedRole==='student'?'border-color:#4A90D9;background-color:#E8F0FE':'border-color:#E8F0FE;background-color:#fff'">
              <svg class="w-8 h-8 mx-auto mb-2" :style="{color:selectedRole==='student'?'#4A90D9':'#1B3A5C'}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0v6m-3-3l3 3 3-3"/>
              </svg>
              <p class="text-sm font-semibold" :style="{color:selectedRole==='student'?'#4A90D9':'#1B3A5C'}">Student</p>
              <p class="text-xs mt-1" style="color:#1B3A5C;opacity:0.6">Find & book tutors</p>
            </button>
            <button @click="selectedRole='tutor'" class="p-4 rounded-xl border-2 text-center transition-all" :style="selectedRole==='tutor'?'border-color:#2EAA4F;background-color:rgba(46,170,79,0.08)':'border-color:#E8F0FE;background-color:#fff'">
              <svg class="w-8 h-8 mx-auto mb-2" :style="{color:selectedRole==='tutor'?'#2EAA4F':'#1B3A5C'}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0H5"/>
              </svg>
              <p class="text-sm font-semibold" :style="{color:selectedRole==='tutor'?'#2EAA4F':'#1B3A5C'}">Tutor</p>
              <p class="text-xs mt-1" style="color:#1B3A5C;opacity:0.6">Teach & earn</p>
            </button>
          </div>
        </div>
        <SignUpButton
          mode="modal"
          :unsafeMetadata="{ role: selectedRole }"
          fallback-redirect-url="/#/dashboard"
        >
          <button class="w-full px-4 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90" :style="{backgroundColor:selectedRole==='tutor'?'#2EAA4F':'#4A90D9'}">
            Sign Up as {{ selectedRole==='tutor'?'Tutor':'Student' }}
          </button>
        </SignUpButton>
        <p class="text-center text-sm mt-6" style="color:#1B3A5C;opacity:0.6">
          Already have an account? <router-link to="/login" class="font-semibold hover:underline" style="color:#4A90D9">Log in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
