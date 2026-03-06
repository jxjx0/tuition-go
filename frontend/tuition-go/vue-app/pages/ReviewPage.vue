<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { StarRating } from '../components'
import { mockSessions } from '../composables/useMockData'

function fmtDate(d: string) { 
  return new Date(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }) 
}

const route = useRoute()
const rating = ref(0)
const comment = ref('')
const submitted = ref(false)
const session = computed(() => mockSessions.find(s => s.id === route.params.sessionId))

const ratingLabel = computed(() => { 
  const l: Record<number, string> = { 1: 'Poor', 2: 'Fair', 3: 'Good', 4: 'Very Good', 5: 'Excellent' }
  return l[rating.value] || '' 
})

function submitReview() { 
  submitted.value = true 
}
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-xl mx-auto px-4 sm:px-6 lg:px-8">
      <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Dashboard
      </router-link>
      <div v-if="session&&!submitted" class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">
        <div class="p-6" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
          <h1 class="text-2xl font-extrabold text-white">Leave a Review</h1>
          <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">Share your experience with {{ session.tutorName }}</p>
        </div>
        <div class="p-6 space-y-6">
          <div class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA">
            <img :src="session.tutorAvatar" :alt="session.tutorName" class="w-14 h-14 rounded-xl" crossorigin="anonymous" style="background-color:#E8F0FE"/>
            <div>
              <p class="font-bold" style="color:#1B3A5C">{{ session.tutorName }}</p>
              <p class="text-sm" style="color:#4A90D9">{{ session.subject }} ({{ session.level }})</p>
              <p class="text-xs mt-0.5" style="color:#1B3A5C;opacity:0.6">{{ fmtDate(session.date) }}</p>
            </div>
          </div>
          <div>
            <label class="text-sm font-bold block mb-3" style="color:#1B3A5C">How would you rate this session?</label>
            <div class="flex items-center gap-4">
              <StarRating v-model:modelValue="rating" :interactive="true" size="lg"/>
              <span v-if="rating" class="text-lg font-bold" style="color:#1B3A5C">{{ ratingLabel }}</span>
            </div>
          </div>
          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Your review</label>
            <textarea v-model="comment" rows="5" placeholder="Tell others about your experience..." class="w-full px-4 py-3 rounded-xl text-sm border resize-none" style="border-color:#E8F0FE;color:#1B3A5C"></textarea>
            <p class="text-xs mt-1 text-right" style="color:#1B3A5C;opacity:0.5">{{ comment.length }}/500</p>
          </div>
          <button @click="submitReview" :disabled="!rating||!comment.trim()" class="w-full py-4 rounded-xl text-base font-bold text-white hover:opacity-90 shadow-md disabled:opacity-40 disabled:cursor-not-allowed" style="background-color:#4A90D9">Submit Review</button>
        </div>
      </div>
      <div v-if="submitted" class="rounded-2xl border p-8 text-center" style="background-color:#fff;border-color:#E8F0FE">
        <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style="background-color:rgba(46,170,79,0.1)">
          <svg class="w-10 h-10" style="color:#2EAA4F" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-extrabold mb-2" style="color:#1B3A5C">Review Submitted!</h2>
        <p class="text-sm mb-6" style="color:#1B3A5C;opacity:0.7">Thank you for your feedback. Your review helps other students find great tutors.</p>
        <router-link to="/dashboard" class="inline-block px-8 py-3 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>
      <div v-if="!session" class="text-center py-20">
        <h2 class="text-2xl font-bold" style="color:#1B3A5C">Session not found</h2>
        <router-link to="/dashboard" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>
