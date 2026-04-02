<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'
import { useSessionService } from '../services/sessionService'
import { useApi } from '../services/api'

interface Session {
  id: string
  tutorId: string
  studentId: string
  tutorSubjectId: string
  startTime: string
  endTime: string
  status: string
  durationMins: number
  meetingLink: string
  createdAt: string
  updatedAt: string
  tutorName: string
  tutorAvatar: string
  subject: string
  level: string
  date: string
  price: number
  notes?: string
}

function toUtcDate(d: string) { return new Date(d + 'Z') }

function fmtDate(d: string) {
  return toUtcDate(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
}

function fmtTime(d: string) {
  return toUtcDate(d).toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

const route = useRoute()
const router = useRouter()
const { user } = useUser()
const session = ref<Session | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const showCancel = ref(false)
const cancelling = ref(false)
const cancelledSuccess = ref(false)
const cancelError = ref<string | null>(null)
const sessionService = useSessionService()
const api = useApi()
const booking = ref(false)

async function bookSession() {
  if (!session.value || !currentStudentId.value) return
  booking.value = true
  try {
    const { data } = await api.post('/checkout/checkout', {
      session_id: session.value.id,
      student_id: currentStudentId.value,
    })
    window.location.href = data.url
  } catch (err) {
    console.error('Failed to initiate booking', err)
    booking.value = false
  }
}

const metadata = computed(() => user.value?.unsafeMetadata as Record<string, unknown> | undefined)
const currentStudentId = computed(() => typeof metadata.value?.studentId === 'string' ? metadata.value.studentId : null)
const userRole = computed(() => typeof metadata.value?.role === 'string' ? metadata.value.role : null)

const isOwner = computed(() =>
  session.value?.status === 'available' ||
  userRole.value === 'tutor' ||
  session.value?.studentId === currentStudentId.value
)

const statusLabel = computed(() => { 
  if (!session.value) return ''
  const m: Record<string, string> = { available: 'Available', booked: 'Upcoming', completed: 'Completed', cancelled: 'Cancelled' }
  return m[session.value.status] || session.value.status 
})

const canCancel = computed(() => {
  if (!session.value || session.value.status !== 'pending') return false
  const now = new Date()
  // The database stores SGT time (e.g. 18:00) as a fixed UTC number (18:00Z).
  // SGT 18:00 is actually 10:00 UTC. To get the real UTC, we subtract 8 hours.
  const startSgt = toUtcDate(session.value.startTime)
  const startUtc = new Date(startSgt.getTime() - (8 * 60 * 60 * 1000))
  const diffHours = (startUtc.getTime() - now.getTime()) / (1000 * 60 * 60)
  return diffHours >= 2
})

const headerStyle = computed(() => { 
  if (!session.value) return ''
  if (session.value.status === 'completed') return 'background:linear-gradient(135deg,#1a6b36 0%,#2EAA4F 100%)'
  if (session.value.status === 'cancelled') return 'background:linear-gradient(135deg,#991b1b 0%,#ef4444 100%)'
  return 'background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)' 
})

async function fetchSession() {
  try {
    loading.value = true
    error.value = null
    const sessionId = route.params.id as string
    const { data } = await sessionService.getSessionById(sessionId)

    session.value = {
      id: data.sessionId,
      tutorId: data.tutorId,
      studentId: data.studentId,
      tutorSubjectId: data.tutorSubjectId,
      startTime: data.startTime,
      endTime: data.endTime,
      status: data.status,
      durationMins: data.durationMins,
      meetingLink: data.meetingLink,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      tutorName: data.tutorName,
      tutorAvatar: data.tutorImageUrl || 'https://via.placeholder.com/56?text=Tutor',
      subject: data.subjectName,
      level: data.academicLevel,
      date: data.startTime,
      price: data.totalPrice
    }
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = 'Session not found'
    } else {
      error.value = 'Failed to load session'
    }
    console.error('Failed to fetch session:', err)
  } finally {
    loading.value = false
  }
}

async function cancelSession() {
  if (!session.value || !currentStudentId.value) return
  cancelling.value = true
  cancelError.value = null
  try {
    await sessionService.cancelSession(session.value.id, currentStudentId.value)
    cancelledSuccess.value = true
    showCancel.value = false
  } catch (err: any) {
    const msg = err.response?.data?.message || 'Failed to cancel session. Please try again.'
    cancelError.value = msg
  } finally {
    cancelling.value = false
  }
}

onMounted(() => {
  fetchSession()
})
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Dashboard
      </router-link>
      <div v-if="loading" class="text-center py-20">
        <svg class="animate-spin w-8 h-8 mx-auto" style="color:#4A90D9" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </div>
      <div v-else-if="error" class="text-center py-20">
        <h2 class="text-2xl font-bold" style="color:#ef4444">{{ error }}</h2>
        <router-link to="/dashboard" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>
      <div v-else-if="!isOwner" class="text-center py-20">
        <h2 class="text-xl font-bold" style="color:#E74C3C">You are not authorised to view this session.</h2>
        <router-link to="/dashboard" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>
      <div v-else-if="cancelledSuccess" class="rounded-2xl border p-12 text-center" style="background-color:#fff;border-color:#E8F0FE">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-3xl font-extrabold mb-4" style="color:#1B3A5C">Cancellation Confirmed</h2>
        <p class="text-lg mb-8" style="color:#1B3A5C;opacity:0.7">Your session has been successfully cancelled and a full refund has been initiated.</p>
        <router-link to="/dashboard" class="inline-block px-8 py-4 rounded-xl text-lg font-bold text-white hover:opacity-90" style="background-color:#4A90D9">Return to Dashboard</router-link>
      </div>
      <div v-else-if="session" class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">
        <div class="p-6" :style="headerStyle">
          <span class="px-3 py-1 rounded-full text-xs font-bold mb-3 inline-block" style="background-color:rgba(255,255,255,0.2);color:#fff">{{ statusLabel }}</span>
          <h1 class="text-2xl font-extrabold text-white">{{ session.subject }} ({{ session.level }})</h1>
          <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">Session with {{ session.tutorName }}</p>
        </div>
        <div class="p-6 space-y-6">
          <div class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA">
            <img :src="session.tutorAvatar" :alt="session.tutorName" class="w-14 h-14 rounded-xl" crossorigin="anonymous" style="background-color:#E8F0FE"/>
            <div class="flex-1">
              <p class="font-bold" style="color:#1B3A5C">{{ session.tutorName }}</p>
              <router-link :to="'/tutors/'+session.tutorId" class="text-xs font-medium hover:underline" style="color:#4A90D9">View Profile</router-link>
            </div>
            <p class="text-xl font-extrabold" style="color:#2EAA4F">${{ session.price.toFixed(2) }}</p>
          </div>
          <div class="rounded-xl p-4 space-y-3" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color:#E8F0FE">
                <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Date</p>
                <p class="text-sm font-bold" style="color:#1B3A5C">{{ fmtDate(session.date) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color:#E8F0FE">
                <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Time</p>
                <p class="text-sm font-bold" style="color:#1B3A5C">
                  {{ fmtTime(session.startTime) }} – {{ fmtTime(session.endTime) }}
                  <span class="font-normal" style="color:#1B3A5C;opacity:0.5">· {{ session.durationMins }} mins</span>
                </p>
              </div>
            </div>
          </div>
          <div v-if="session.notes" class="p-4 rounded-xl" style="background-color:#F5F7FA">
            <p class="text-xs font-semibold mb-1" style="color:#1B3A5C">Session Notes</p>
            <p class="text-sm" style="color:#1B3A5C;opacity:0.8">{{ session.notes }}</p>
          </div>
          <div v-if="session.meetingLink&&session.status==='booked'" class="p-4 rounded-xl border" style="border-color:#E8F0FE">
            <p class="text-xs font-semibold mb-2" style="color:#1B3A5C">Google Meet</p>
            <a :href="session.meetingLink" target="_blank" class="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90" style="background-color:#2EAA4F">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
              </svg>
              Join Meeting
            </a>
          </div>
          <div class="flex flex-col sm:flex-row gap-3">
            <button v-if="session.status==='available'&&userRole!=='tutor'" @click="bookSession" :disabled="booking" class="flex-1 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2" style="background-color:#2EAA4F">
  <svg v-if="booking" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
  </svg>
  {{ booking ? 'Processing...' : 'Book Session' }}
</button>
            <button v-if="session.status==='pending'&&!showCancel&&userRole==='student'" @click="showCancel=true" :disabled="!canCancel" :class="[!canCancel ? 'opacity-50 cursor-not-allowed grayscale' : 'hover:bg-red-50']" class="flex-1 py-3 rounded-xl text-sm font-semibold border" style="border-color:#ef4444;color:#ef4444">
              {{ canCancel ? 'Cancel Session' : 'Cancellation Unavailable (< 2h)' }}
            </button>
            <router-link v-if="session.status==='completed'&&userRole==='student'" :to="'/review/'+session.id" class="flex-1 py-3 rounded-xl text-sm font-semibold text-white text-center hover:opacity-90" style="background-color:#4A90D9">Leave a Review</router-link>
          </div>
          <div v-if="showCancel" class="p-5 rounded-xl border" style="border-color:#ef4444;background-color:rgba(239,68,68,0.03)">
            <p class="text-sm font-bold mb-1" style="color:#ef4444">Cancel this session?</p>
            <p class="text-xs mb-4" style="color:#1B3A5C;opacity:0.7">A full refund will be processed within 3-5 business days.</p>
            <!-- Error from backend (e.g. < 2-hour window) -->
            <div v-if="cancelError" class="mb-3 p-3 rounded-lg text-xs font-medium" style="background-color:rgba(239,68,68,0.08);color:#ef4444">{{ cancelError }}</div>
            <div class="flex gap-3">
              <button
                @click="cancelSession"
                :disabled="cancelling"
                class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                style="background-color:#ef4444"
              >
                <svg v-if="cancelling" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ cancelling ? 'Cancelling...' : 'Yes, Cancel' }}
              </button>
              <button @click="showCancel=false; cancelError=null" :disabled="cancelling" class="px-6 py-2.5 rounded-xl text-sm font-semibold border disabled:opacity-60" style="border-color:#E8F0FE;color:#1B3A5C">Keep Session</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-20">
        <h2 class="text-2xl font-bold" style="color:#1B3A5C">Session not found</h2>
        <router-link to="/dashboard" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>
