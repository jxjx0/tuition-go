<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUser } from '@clerk/vue'
import { StarRating } from '../components'
import { mockSessions, mockReviews } from '../composables/useMockData'

function fmtDate(d: string) { 
  return new Date(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short' }) 
}

const showCreateSlot = ref(false)
const { user } = useUser()
const tutorId = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  return typeof metadata?.tutorId === 'string' ? metadata.tutorId : null
})

const tutorSessions = computed(() => {
  if (!tutorId.value) return []
  return mockSessions.filter(s => s.tutorId === tutorId.value)
})
const tutorUpcoming = computed(() => tutorSessions.value.filter(s => s.status === 'booked' || s.status === 'available'))
const tutorReviews = computed(() => {
  if (!tutorId.value) return []
  return mockReviews.filter(r => r.tutorId === tutorId.value)
})

const tutorStats = [
  { value: '340', label: 'Total Sessions', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { value: '$22,100', label: 'Total Earnings', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
  { value: '4.9', label: 'Average Rating', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { value: '127', label: 'Total Reviews', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
]
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold" style="color:#1B3A5C">Tutor Dashboard</h1>
          <p class="mt-1 text-base" style="color:#1B3A5C;opacity:0.6">Welcome back, James. Manage your sessions and availability.</p>
        </div>
        <button @click="showCreateSlot=!showCreateSlot" class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90" style="background-color:#2EAA4F">+ Create Session Slot</button>
      </div>
      <div v-if="showCreateSlot" class="rounded-2xl border p-6 mb-8" style="background-color:#fff;border-color:#E8F0FE">
        <h3 class="text-lg font-bold mb-4" style="color:#1B3A5C">New Session Slot</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Subject</label>
            <select class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C">
              <option>Mathematics (A-Level)</option>
              <option>Mathematics (O-Level)</option>
              <option>Further Mathematics (A-Level)</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Date</label>
            <input type="date" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Time</label>
            <div class="flex items-center gap-2">
              <input type="time" class="flex-1 px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
              <span class="text-xs" style="color:#1B3A5C;opacity:0.5">to</span>
              <input type="time" class="flex-1 px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3 mt-4">
          <button @click="showCreateSlot=false" class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white" style="background-color:#2EAA4F">Create Slot</button>
          <button @click="showCreateSlot=false" class="px-6 py-2.5 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">Cancel</button>
        </div>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div v-for="stat in tutorStats" :key="stat.label" class="rounded-2xl border p-5" style="background-color:#fff;border-color:#E8F0FE">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-3" :style="{backgroundColor:stat.bg}">
            <svg class="w-5 h-5" :style="{color:stat.iconColor}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-2xl font-extrabold" style="color:#1B3A5C">{{ stat.value }}</p>
          <p class="text-xs font-medium mt-0.5" style="color:#1B3A5C;opacity:0.6">{{ stat.label }}</p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
          <h2 class="text-lg font-bold mb-4" style="color:#1B3A5C">Upcoming Sessions</h2>
          <div class="space-y-3">
            <div v-for="session in tutorUpcoming" :key="session.id" class="rounded-2xl border p-5 hover:shadow-sm" style="background-color:#fff;border-color:#E8F0FE">
              <div class="flex items-start gap-4">
                <img :src="session.studentAvatar||'https://api.dicebear.com/9.x/notionists/svg?seed=Default'" :alt="session.studentName" class="w-12 h-12 rounded-xl flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"/>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-bold" style="color:#1B3A5C">{{ session.subject }} ({{ session.level }})</h3>
                  <p class="text-xs mt-0.5" style="color:#1B3A5C;opacity:0.7">with {{ session.studentName||'Available' }}</p>
                  <div class="flex flex-wrap items-center gap-3 mt-2 text-xs" style="color:#1B3A5C;opacity:0.6">
                    <span>{{ fmtDate(session.date) }}</span>
                    <span>{{ session.startTime }} - {{ session.endTime }}</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 flex-shrink-0 items-end">
                  <span class="text-sm font-bold" style="color:#2EAA4F">${{ session.price.toFixed(2) }}</span>
                  <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold" :style="session.status==='booked'?'background-color:#E8F0FE;color:#4A90D9':'background-color:rgba(46,170,79,0.1);color:#2EAA4F'">{{ session.status==='booked'?'Booked':'Open' }}</span>
                </div>
              </div>
            </div>
            <div v-if="!tutorUpcoming.length" class="text-center py-12 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
              <p class="text-sm" style="color:#1B3A5C;opacity:0.6">No upcoming sessions</p>
            </div>
          </div>
        </div>
        <div>
          <h2 class="text-lg font-bold mb-4" style="color:#1B3A5C">Recent Reviews</h2>
          <div class="space-y-3">
            <div v-for="review in tutorReviews" :key="review.id" class="rounded-2xl border p-4" style="background-color:#fff;border-color:#E8F0FE">
              <div class="flex items-center gap-2 mb-2">
                <img :src="review.studentAvatar" :alt="review.studentName" class="w-8 h-8 rounded-full" crossorigin="anonymous"/>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold truncate" style="color:#1B3A5C">{{ review.studentName }}</p>
                  <StarRating :modelValue="review.rating" size="sm"/>
                </div>
              </div>
              <p class="text-xs leading-relaxed" style="color:#1B3A5C;opacity:0.75;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">{{ review.comment }}</p>
              <p class="text-xs mt-2" style="color:#1B3A5C;opacity:0.45">{{ review.subject }} &middot; {{ fmtDate(review.createdAt) }}</p>
            </div>
            <div v-if="!tutorReviews.length" class="text-center py-8 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
              <p class="text-sm" style="color:#1B3A5C;opacity:0.6">No reviews yet</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
