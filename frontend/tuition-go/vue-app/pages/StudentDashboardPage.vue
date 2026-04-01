<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUser } from '@clerk/vue'
import { useSessionService } from '../services/sessionService'

interface Session {
  id: string
  tutorName: string
  tutorAvatar: string | null
  subject: string
  level: string
  date: string
  startTime: string
  endTime: string
  price: number
  status: string
  meetingLink: string | null
  notes: string | null
  durationMins: number
}

function fmtDate(d: string) { 
  return new Date(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short' })
}

function fmtTime(d: string) {
  return new Date(d).toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', hour12: true })
}

const activeTab = ref('upcoming')
const { user, isLoaded } = useUser()
const currentStudentId = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  return typeof metadata?.studentId === 'string' ? metadata.studentId : null
})

const sessions = ref<Session[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const sessionService = useSessionService()

// Cancel state
const showCancelId = ref<string | null>(null)   // which session's confirm dialog is open
const cancellingId = ref<string | null>(null)    // which session is being cancelled right now
const cancelError  = ref<string | null>(null)    // error message from backend
const cancelSuccess = ref<boolean>(false)         // show success toast/banner

const fetchSessions = async () => {
  if (!currentStudentId.value) {
    sessions.value = []
    error.value = 'Student profile is not linked to this account yet.'
    return
  }

  loading.value = true
  error.value = null
  try {
    const { data } = await sessionService.getStudentSessions(currentStudentId.value)

    // Transform the API response to match the component's expected format
    sessions.value = data.map((session: any) => ({
      id: session.sessionId,
      tutorName: session.tutorName || 'Unknown Tutor',
      tutorAvatar: session.tutorImageUrl || 'https://via.placeholder.com/56',
      subject: session.subjectName || 'Unknown Subject',
      level: session.academicLevel || 'Unknown',
      date: session.startTime,
      startTime: fmtTime(session.startTime),
      endTime: fmtTime(session.endTime),
      price: session.totalPrice || 0,
      status: session.status || 'pending',
      meetingLink: session.meetingLink,
      notes: null,
      durationMins: session.durationMins || 0
    }))
  } catch (err: any) {
    if (err.response?.status === 404) {
      sessions.value = []
      return
    }
    error.value = err.message
    console.error('Error fetching sessions:', err)
    sessions.value = []
  } finally {
    loading.value = false
  }
}

const upcomingSessions = computed(() => {
  return sessions.value.filter(s => s.status === 'booked')
})

const pastSessions = computed(() => {
  return sessions.value.filter(s => s.status === 'completed')
})

const cancelledSessions = computed(() => {
  return sessions.value.filter(s => s.status === 'cancelled')
})

watch(
  () => [isLoaded.value, currentStudentId.value],
  ([loaded, studentId]) => {
    if (loaded && studentId) {
      fetchSessions()
    }
  },
  { immediate: true }
)

async function cancelSession(sessionId: string) {
  if (!currentStudentId.value) return
  cancellingId.value = sessionId
  cancelError.value = null
  try {
    await sessionService.cancelSession(sessionId, currentStudentId.value)
    showCancelId.value = null
    cancelSuccess.value = true
    setTimeout(() => { cancelSuccess.value = false }, 5000)
    await fetchSessions()   // refresh the list
  } catch (err: any) {
    cancelError.value = err.response?.data?.message || 'Failed to cancel. Please try again.'
  } finally {
    cancellingId.value = null
  }
}

const tabs = computed(() => [
  { key: 'upcoming', label: 'Upcoming', count: upcomingSessions.value.length },
])

const dashStats = computed(() => {
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  
  const completedThisMonth = pastSessions.value.filter(s => {
    const sessionDate = new Date(s.date)
    return sessionDate.getMonth() === currentMonth && sessionDate.getFullYear() === currentYear
  })
  
  const hoursCompletedThisMonth = completedThisMonth.reduce((sum, s) => sum + s.durationMins, 0) / 60
  
  return [
    { value: String(upcomingSessions.value.length), label: 'Upcoming Sessions', bg: '#E8F0FE', iconColor: '#4A90D9' },
    { value: String(pastSessions.value.length), label: 'Completed', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
    { value: `${hoursCompletedThisMonth.toFixed(1)}h`, label: 'Hours This Month', bg: '#E8F0FE', iconColor: '#4A90D9' },
  ]
})
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold" style="color:#1B3A5C">Welcome back, {{ user?.firstName ?? 'Student' }}</h1>
          <p class="mt-1 text-base" style="color:#1B3A5C;opacity:0.6">Here is a summary of your learning journey</p>
        </div>
        <router-link to="/tutors" class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90" style="background-color:#4A90D9">Book New Session</router-link>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        <div v-for="stat in dashStats" :key="stat.label" class="rounded-2xl border p-5" style="background-color:#fff;border-color:#E8F0FE">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-3" :style="{backgroundColor:stat.bg}">
            <svg class="w-5 h-5" :style="{color:stat.iconColor}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-2xl font-extrabold" style="color:#1B3A5C">{{ stat.value }}</p>
          <p class="text-xs font-medium mt-0.5" style="color:#1B3A5C;opacity:0.6">{{ stat.label }}</p>
        </div>
      </div>
      <!-- Global Success Banner for Cancellation — outside session list so it shows even if list becomes empty -->
      <transition name="slide-up">
        <div v-if="cancelSuccess" class="mb-6 rounded-2xl border-l-4 border-emerald-500 bg-emerald-50 p-6 shadow-md flex items-center gap-4">
          <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <div>
            <h3 class="text-emerald-900 font-bold">Cancellation Successful</h3>
            <p class="text-emerald-700 text-sm">Your session has been cancelled and a full refund has been initiated via Stripe. Refunds typically take 3–5 business days.</p>
          </div>
          <button @click="cancelSuccess = false" class="ml-auto text-emerald-500 hover:text-emerald-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </transition>

      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin">
          <svg class="w-8 h-8" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </div>
        <p class="mt-4" style="color:#1B3A5C">Loading your sessions...</p>
      </div>
      <div v-else-if="error" class="text-center py-20 rounded-2xl border p-8" style="background-color:#fff;border-color:#E8F0FE">
        <h2 class="text-xl font-bold mb-2" style="color:#ef4444">Error loading sessions</h2>
        <p class="mb-4" style="color:#1B3A5C;opacity:0.7">{{ error }}</p>
        <button @click="fetchSessions" class="px-6 py-2 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Try Again</button>
      </div>
      <div v-else-if="sessions.length === 0" class="text-center py-20 rounded-2xl border p-8" style="background-color:#fff;border-color:#E8F0FE">
        <h2 class="text-xl font-bold mb-2" style="color:#1B3A5C">No sessions yet</h2>
        <p class="mb-4" style="color:#1B3A5C;opacity:0.7">Start your learning journey by booking a session with a tutor</p>
        <router-link to="/tutors" class="inline-block px-6 py-2 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Browse Tutors</router-link>
      </div>
      <div v-else class="space-y-4">
        <div v-for="session in upcomingSessions" :key="session.id" class="rounded-2xl border p-5 hover:shadow-sm" style="background-color:#fff;border-color:#E8F0FE">
          <div class="flex flex-col sm:flex-row items-start gap-4">
            <img :src="session.tutorAvatar || undefined" :alt="session.tutorName" class="w-14 h-14 rounded-xl object-cover flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"/>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-bold" style="color:#1B3A5C">{{ session.subject }} ({{ session.level }})</h3>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold" style="background-color:#E8F0FE;color:#4A90D9">Upcoming</span>
              </div>
              <p class="text-sm mt-1" style="color:#1B3A5C;opacity:0.7">with {{ session.tutorName }}</p>
              <div class="flex flex-wrap items-center gap-4 mt-3 text-xs" style="color:#1B3A5C;opacity:0.6">
                <span>{{ fmtDate(session.date) }}</span>
                <span>{{ session.startTime }} - {{ session.endTime }}</span>
                <span class="font-semibold" style="color:#2EAA4F">${{ session.price.toFixed(2) }}</span>
              </div>
              <p v-if="session.notes" class="mt-2 text-xs px-3 py-1.5 rounded-lg" style="background-color:#F5F7FA;color:#1B3A5C;opacity:0.7">{{ session.notes }}</p>
            </div>
            <div class="flex flex-row sm:flex-col gap-2 flex-shrink-0">
              <a v-if="session.meetingLink" :href="session.meetingLink" target="_blank" class="px-4 py-2 rounded-xl text-xs font-semibold text-white text-center hover:opacity-90" style="background-color:#2EAA4F">Join Meeting</a>
              <router-link :to="'/session/'+session.id" class="px-4 py-2 rounded-xl text-xs font-semibold text-center border hover:bg-gray-50" style="border-color:#E8F0FE;color:#4A90D9">Details</router-link>
              <button
                @click="showCancelId = session.id; cancelError = null"
                class="px-4 py-2 rounded-xl text-xs font-semibold border hover:bg-red-50"
                style="border-color:#ef4444;color:#ef4444"
              >Cancel</button>
            </div>
          </div>
          <!-- Inline cancel confirmation for this card -->
          <div v-if="showCancelId === session.id" class="mt-3 p-4 rounded-xl border" style="border-color:#ef4444;background-color:rgba(239,68,68,0.03)">
            <p class="text-xs font-bold mb-1" style="color:#ef4444">Cancel this session?</p>
            <p class="text-xs mb-3" style="color:#1B3A5C;opacity:0.7">Cancellation must be made at least 2 hours in advance. A full refund will be issued within 3–5 business days.</p>
            <div v-if="cancelError && cancellingId === null && showCancelId === session.id" class="mb-2 p-2 rounded-lg text-xs font-medium" style="background-color:rgba(239,68,68,0.08);color:#ef4444">{{ cancelError }}</div>
            <div class="flex gap-2">
              <button
                @click="cancelSession(session.id)"
                :disabled="cancellingId === session.id"
                class="px-4 py-2 rounded-xl text-xs font-semibold text-white flex items-center gap-1.5 disabled:opacity-60 disabled:cursor-not-allowed"
                style="background-color:#ef4444"
              >
                <svg v-if="cancellingId === session.id" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ cancellingId === session.id ? 'Cancelling...' : 'Yes, Cancel' }}
              </button>
              <button
                @click="showCancelId = null; cancelError = null"
                :disabled="cancellingId === session.id"
                class="px-4 py-2 rounded-xl text-xs font-semibold border disabled:opacity-60"
                style="border-color:#E8F0FE;color:#1B3A5C"
              >Keep</button>
            </div>
          </div>
        </div>
        <div v-if="!upcomingSessions.length" class="text-center py-16 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
          <p class="text-base font-semibold" style="color:#1B3A5C">No upcoming sessions</p>
          <router-link to="/tutors" class="inline-block mt-4 px-6 py-2.5 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Find Tutors</router-link>
      </div>
      </div>
    </div>
  </div>
</template>
