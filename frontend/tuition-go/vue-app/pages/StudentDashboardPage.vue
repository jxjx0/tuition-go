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
  return sessions.value.filter(s => s.status !== 'completed' && s.status !== 'cancelled')
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

const tabs = computed(() => [
  { key: 'upcoming', label: 'Upcoming', count: upcomingSessions.value.length },
  { key: 'past', label: 'Completed', count: pastSessions.value.length },
  { key: 'cancelled', label: 'Cancelled', count: cancelledSessions.value.length },
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
      <div v-else>
        <div class="flex items-center gap-1 p-1 rounded-xl mb-6" style="background-color:#E8F0FE">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab=tab.key" class="flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all" :style="activeTab===tab.key?'background-color:#fff;color:#4A90D9;box-shadow:0 1px 3px rgba(0,0,0,0.08)':'color:#1B3A5C;opacity:0.7'">{{ tab.label }} ({{ tab.count }})</button>
        </div>
      <div v-if="activeTab==='upcoming'" class="space-y-4">
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
            </div>
          </div>
        </div>
        <div v-if="!upcomingSessions.length" class="text-center py-16 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
          <p class="text-base font-semibold" style="color:#1B3A5C">No upcoming sessions</p>
          <router-link to="/tutors" class="inline-block mt-4 px-6 py-2.5 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Find Tutors</router-link>
        </div>
      </div>
      <div v-if="activeTab==='past'" class="space-y-4">
        <div v-for="session in pastSessions" :key="session.id" class="rounded-2xl border p-5 hover:shadow-sm" style="background-color:#fff;border-color:#E8F0FE">
          <div class="flex flex-col sm:flex-row items-start gap-4">
            <img :src="session.tutorAvatar || undefined" :alt="session.tutorName" class="w-14 h-14 rounded-xl object-cover flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"/>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-bold" style="color:#1B3A5C">{{ session.subject }} ({{ session.level }})</h3>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold" style="background-color:rgba(46,170,79,0.1);color:#2EAA4F">Completed</span>
              </div>
              <p class="text-sm mt-1" style="color:#1B3A5C;opacity:0.7">with {{ session.tutorName }}</p>
              <div class="flex flex-wrap items-center gap-4 mt-2 text-xs" style="color:#1B3A5C;opacity:0.6">
                <span>{{ fmtDate(session.date) }}</span>
                <span>{{ session.startTime }} - {{ session.endTime }}</span>
                <span class="font-semibold" style="color:#2EAA4F">${{ session.price.toFixed(2) }}</span>
              </div>
            </div>
            <router-link :to="'/review/'+session.id" class="px-4 py-2 rounded-xl text-xs font-semibold text-white text-center hover:opacity-90 flex-shrink-0" style="background-color:#4A90D9">Leave Review</router-link>
          </div>
        </div>
      </div>
      <div v-if="activeTab==='cancelled'" class="space-y-4">
        <div v-for="session in cancelledSessions" :key="session.id" class="rounded-2xl border p-5 opacity-70" style="background-color:#fff;border-color:#E8F0FE">
          <div class="flex flex-col sm:flex-row items-start gap-4">
            <img :src="session.tutorAvatar || undefined" :alt="session.tutorName" class="w-14 h-14 rounded-xl object-cover flex-shrink-0 grayscale" crossorigin="anonymous" style="background-color:#E8F0FE"/>
            <div class="flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-bold" style="color:#1B3A5C">{{ session.subject }} ({{ session.level }})</h3>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold" style="background-color:rgba(239,68,68,0.1);color:#ef4444">Cancelled</span>
              </div>
              <p class="text-sm mt-1" style="color:#1B3A5C;opacity:0.7">with {{ session.tutorName }}</p>
              <p class="text-xs mt-2" style="color:#1B3A5C;opacity:0.6">{{ fmtDate(session.date) }} &middot; {{ session.startTime }} - {{ session.endTime }}</p>
            </div>
          </div>
        </div>
        <div v-if="!cancelledSessions.length" class="text-center py-16 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
          <p class="text-sm" style="color:#1B3A5C;opacity:0.6">No cancelled sessions</p>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>
