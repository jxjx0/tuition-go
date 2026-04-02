<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUser } from '@clerk/vue'
import { StarRating } from '../components'
import { findTutorById } from "../composables/useTutors"
import { useSessionService } from '../services/sessionService'
import { useApi } from '../services/api'
import { avatarUrl } from '../utils/avatar'

function toUtcDate(d: string) {
  return new Date(/[Zz]$|[+-]\d{2}:?\d{2}$/.test(d) ? d : d + 'Z')
}

function fmtDate(d: string) {
  return toUtcDate(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })
}

function fmtTime(d: string) {
  return toUtcDate(d).toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

const { user } = useUser()

const showCreateSlot = ref(false)

const sessionService = useSessionService()
const slotForm = ref({ tutorSubjectId: '', date: '', startTime: '', endTime: '' })
const slotError = ref('')
const slotCreating = ref(false)

// Generate time options in 15-min increments (00:00 – 23:45)
const timeOptions = Array.from({ length: 96 }, (_, i) => {
  const h = Math.floor(i / 4).toString().padStart(2, '0')
  const m = ((i % 4) * 15).toString().padStart(2, '0')
  const value = `${h}:${m}`
  const hour = Math.floor(i / 4)
  const ampm = hour < 12 ? 'AM' : 'PM'
  const h12 = (hour % 12 || 12).toString()
  const label = `${h12}:${m} ${ampm}`
  return { value, label }
})

const slotDuration = computed(() => {
  if (!slotForm.value.startTime || !slotForm.value.endTime) return null
  const [sh, sm] = slotForm.value.startTime.split(':').map(Number)
  const [eh, em] = slotForm.value.endTime.split(':').map(Number)
  const mins = (eh * 60 + em) - (sh * 60 + sm)
  if (mins <= 0) return null
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h > 0 ? (m > 0 ? `${h}h ${m}m` : `${h}h`) : `${m}m`
})

async function handleCreateSlot() {
  slotError.value = ''
  if (!slotForm.value.tutorSubjectId || !slotForm.value.date || !slotForm.value.startTime || !slotForm.value.endTime) {
    slotError.value = 'Please fill in all fields'
    return
  }
  const startTime = `${slotForm.value.date}T${slotForm.value.startTime}:00`
  const endTime = `${slotForm.value.date}T${slotForm.value.endTime}:00`
  const durationMins = (new Date(endTime).getTime() - new Date(startTime).getTime()) / 60000
  if (durationMins <= 0) {
    slotError.value = 'End time must be after start time'
    return
  }

  // Find the subject name for the meeting summary
  const selectedSubject = tutor.value?.subjects?.find(s => s.tutorSubjectId === slotForm.value.tutorSubjectId)
  const subjectLabel = selectedSubject ? `${selectedSubject.subject} (${selectedSubject.academicLevel})` : 'Tutor Session'

  slotCreating.value = true
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    await sessionService.createSessionWithCalendar({
      tutorId: tutorId.value!,
      tutorSubjectId: slotForm.value.tutorSubjectId,
      startTime,
      endTime,
      durationMins,
      summary: subjectLabel,
      timezone: tz,
    })

    slotForm.value = { tutorSubjectId: '', date: '', startTime: '', endTime: '' }
    showCreateSlot.value = false
    if (tutorId.value) fetchSessions(tutorId.value)
  } catch (err: any) {
    slotError.value = err?.response?.data?.message || err?.response?.data?.error || 'Failed to create session slot'
  } finally {
    slotCreating.value = false
  }
}

const tutorId = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  return typeof metadata?.tutorId === 'string' ? metadata.tutorId : null
})
const { tutor, searchForTutor } = findTutorById()

const sessions = ref<any[]>([])
const sessionsLoading = ref(false)
const sessionTab = ref<'booked' | 'available' | 'completed'>('booked')

async function fetchSessions(id: string) {
  sessionsLoading.value = true
  try {
    const { data } = await sessionService.getTutorSessions(id)
    sessions.value = data
  } catch (err) {
    console.error('Failed to fetch sessions', err)
  } finally {
    sessionsLoading.value = false
  }
}

const api = useApi()
const tutorReviews = ref<any[]>([])

async function fetchReviews(id: string) {
  try {
    const { data } = await api.get(`/get-tutor/${id}`)
    tutorReviews.value = data?.reviews ?? []
  } catch {
    tutorReviews.value = []
  }
}

function isBookedSession(session: any) {
  const st = (session.status || '').toLowerCase()
  return st === 'pending' || st === 'booked' || st === 'confirmed'
}

function isAvailableSession(session: any) {
  const st = (session.status || '').toLowerCase()
  return st === 'available'
}

function isCompletedSession(session: any) {
  const st = (session.status || '').toLowerCase()
  return st === 'completed'
}

const bookedSessions = computed(() => sessions.value.filter(isBookedSession))
const availableSessions = computed(() => sessions.value.filter(isAvailableSession))
const completedSessions = computed(() => sessions.value.filter(isCompletedSession))

const sessionTabs = computed(() => [
  { key: 'booked',    label: 'Booked',    count: bookedSessions.value.length },
  { key: 'available', label: 'Available', count: availableSessions.value.length },
  { key: 'completed', label: 'Completed', count: completedSessions.value.length },
])

const displayedSessions = computed(() => {
  if (sessionTab.value === 'available') return availableSessions.value
  if (sessionTab.value === 'completed') return completedSessions.value
  return bookedSessions.value
})

watch(tutorId, (id) => {
  if (id) {
    searchForTutor(id)
    fetchSessions(id)
    fetchReviews(id)
  }
}, { immediate: true })

const tutorStats = computed(() => [
  { value: '340',                                              label: 'Total Sessions', bg: '#E8F0FE',              iconColor: '#4A90D9' },
  { value: '$22,100',                                          label: 'Total Earnings', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
  { value: tutor.value?.averageRating?.toFixed(1) ?? '0.0',   label: 'Average Rating', bg: '#E8F0FE',              iconColor: '#4A90D9' },
  { value: String(tutor.value?.totalReviews ?? '0'),           label: 'Total Reviews',  bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
])
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold" style="color:#1B3A5C">Tutor Dashboard</h1>
          <p class="mt-1 text-base" style="color:#1B3A5C;opacity:0.6">Welcome back, James. Manage your sessions and availability.</p>
        </div>
        <div class="flex gap-4">
          <button @click="showCreateSlot=!showCreateSlot" class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90" style="background-color:#2EAA4F">+ Create Session Slot</button>
        </div>
      </div>

      <div v-if="showCreateSlot" class="rounded-2xl border p-6 mb-8" style="background-color:#fff;border-color:#E8F0FE">
        <h3 class="text-lg font-bold mb-5" style="color:#1B3A5C">New Session Slot</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Subject -->
          <div>
            <label class="text-xs font-semibold uppercase mb-1.5 block" style="color:#1B3A5C;opacity:0.5">Subject</label>
            <select v-model="slotForm.tutorSubjectId" class="w-full px-4 py-2.5 rounded-xl text-sm border focus:outline-none" style="border-color:#E8F0FE;color:#1B3A5C">
              <option value="" disabled>Select subject</option>
              <option v-for="s in tutor?.subjects" :key="s.tutorSubjectId" :value="s.tutorSubjectId">
                {{ s.subject }} ({{ s.academicLevel }})
              </option>
            </select>
          </div>
          <!-- Date -->
          <div>
            <label class="text-xs font-semibold uppercase mb-1.5 block" style="color:#1B3A5C;opacity:0.5">Date</label>
            <input v-model="slotForm.date" type="date" class="w-full px-4 py-2.5 rounded-xl text-sm border focus:outline-none" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <!-- Start time -->
          <div>
            <label class="text-xs font-semibold uppercase mb-1.5 block" style="color:#1B3A5C;opacity:0.5">Start Time</label>
            <select v-model="slotForm.startTime" class="w-full px-4 py-2.5 rounded-xl text-sm border focus:outline-none" style="border-color:#E8F0FE;color:#1B3A5C">
              <option value="" disabled>Select start time</option>
              <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
          <!-- End time -->
          <div>
            <label class="text-xs font-semibold uppercase mb-1.5 block" style="color:#1B3A5C;opacity:0.5">End Time</label>
            <select v-model="slotForm.endTime" class="w-full px-4 py-2.5 rounded-xl text-sm border focus:outline-none" style="border-color:#E8F0FE;color:#1B3A5C">
              <option value="" disabled>Select end time</option>
              <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
        </div>
        <!-- Duration pill -->
        <div v-if="slotDuration" class="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold" style="background-color:#E8F0FE;color:#4A90D9">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ slotDuration }}
        </div>
        <p v-if="slotError" class="mt-3 text-xs" style="color:#E74C3C">{{ slotError }}</p>
        <div class="flex items-center gap-3 mt-5">
          <button @click="handleCreateSlot" :disabled="slotCreating" class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-50 flex items-center gap-2" style="background-color:#2EAA4F">
            <svg v-if="slotCreating" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ slotCreating ? 'Creating...' : 'Create Slot' }}
          </button>
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
          <h2 class="text-lg font-bold mb-4" style="color:#1B3A5C">Sessions</h2>
          <div class="flex items-center gap-1 p-1 rounded-xl mb-6" style="background-color:#E8F0FE">
            <button v-for="tab in sessionTabs" :key="tab.key" @click="sessionTab = tab.key as any" class="flex-1 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all" :style="sessionTab===tab.key?'background-color:#fff;color:#4A90D9;box-shadow:0 1px 3px rgba(0,0,0,0.08)':'color:#1B3A5C;opacity:0.7'">
              {{ tab.label }} ({{ tab.count }})
            </button>
          </div>
          <div v-if="sessionsLoading" class="text-center py-12 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
            <svg class="animate-spin w-6 h-6 mx-auto" style="color:#4A90D9" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
          </div>
          <div v-else class="space-y-3">
            <div v-for="session in displayedSessions" :key="session.sessionId" class="rounded-2xl border p-5 hover:shadow-sm cursor-pointer" :class="session.status==='cancelled'?'opacity-60':''" style="background-color:#fff;border-color:#E8F0FE" @click="$router.push(`/tutor-session/${session.sessionId}`)">
              <div class="flex items-start gap-4">
                <img
                  :src="avatarUrl(isBookedSession(session) ? session.studentImageUrl : null, session.studentId || 'default')"
                  class="w-12 h-12 rounded-xl object-cover flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"
                />
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-bold" style="color:#1B3A5C">{{ session.subjectName }} ({{ session.academicLevel }})</h3>
                  <p class="text-xs mt-0.5" style="color:#1B3A5C;opacity:0.7">{{ isBookedSession(session) ? (session.studentName ? 'with ' + session.studentName : 'Student #' + session.studentId?.slice(0, 8)) : '' }}</p>
                  <div class="flex flex-wrap items-center gap-3 mt-2 text-xs" style="color:#1B3A5C;opacity:0.6">
                    <span>{{ fmtDate(session.startTime) }}</span>
                    <span>{{ fmtTime(session.startTime) }} - {{ fmtTime(session.endTime) }}</span>
                    <span v-if="session.durationMins">{{ session.durationMins }} mins</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 flex-shrink-0 items-end">
                  <span v-if="session.totalPrice" class="text-sm font-bold" style="color:#2EAA4F">${{ session.totalPrice.toFixed(2) }}</span>
                  <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
                    :style="isBookedSession(session) ? 'background-color:#E8F0FE;color:#4A90D9'
                          : isCompletedSession(session) ? 'background-color:rgba(124,58,237,0.1);color:#7C3AED'
                          : 'background-color:rgba(46,170,79,0.1);color:#2EAA4F'"
                  >{{ isBookedSession(session) ? 'Booked' : isCompletedSession(session) ? 'Completed' : 'Available' }}</span>
                </div>
              </div>
            </div>
            <div v-if="!displayedSessions.length" class="text-center py-12 rounded-2xl border" style="background-color:#fff;border-color:#E8F0FE">
              <p class="text-sm" style="color:#1B3A5C;opacity:0.6">No {{ sessionTab }} sessions</p>
            </div>
          </div>
        </div>
        <div>
          <h2 class="text-lg font-bold mb-4" style="color:#1B3A5C">Recent Reviews</h2>
          <div class="space-y-3">
            <div v-for="review in tutorReviews" :key="review.review_id" class="rounded-2xl border p-4" style="background-color:#fff;border-color:#E8F0FE">
              <div class="flex items-center gap-2 mb-2">
                <img :src="avatarUrl(review.studentAvatar, review.student_id)" class="w-8 h-8 rounded-full" crossorigin="anonymous"/>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold" style="color:#1B3A5C">{{ review.studentName || 'Anonymous' }}</p>
                  <StarRating :modelValue="review.rating" size="sm"/>
                </div>
              </div>
              <p class="text-xs leading-relaxed" style="color:#1B3A5C;opacity:0.75;display:-webkit-box;-webkit-line-clamp:3;line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">{{ review.comment }}</p>
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
