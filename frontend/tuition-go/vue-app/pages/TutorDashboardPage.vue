<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUser } from '@clerk/vue'
import { StarRating } from '../components'
import { useMeeting } from '../composables/useMeeting'
import { mockSessions, mockReviews } from '../composables/useMockData'
import { findTutorById } from "../composables/useTutors"
import { useSessionService } from '../services/sessionService'

function fmtDate(d: string) { 
  return new Date(d).toLocaleDateString('en-SG', { weekday: 'short', day: 'numeric', month: 'short' }) 
}


const { user } = useUser()
const { loading: meetingLoading, error: meetingError, result: meetingResult, createMeeting } = useMeeting()

const meetingForm = ref({
  summary: 'Tutor Session',
  description: '',
  date: '',
  startTime: '',
  endTime: ''
})

async function handleCreateMeeting() {
  try {
    const start = `${meetingForm.value.date}T${meetingForm.value.startTime}:00Z`
    const end = `${meetingForm.value.date}T${meetingForm.value.endTime}:00Z`
    
    await createMeeting({
      summary: meetingForm.value.summary,
      description: meetingForm.value.description,
      start_time: start,
      end_time: end,
      attendees: [] // Optional: fetch student email if linked to a specific session
    })
    
    showCreateMeeting.value = false
  } catch (err) {
    console.error('Meeting creation failed:', err)
  }
}

const showCreateSlot = ref(false)
const showCreateMeeting = ref(false)

const sessionService = useSessionService()
const slotForm = ref({ tutorSubjectId: '', date: '', startTime: '', endTime: '' })
const slotError = ref('')
const slotCreating = ref(false)

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
  slotCreating.value = true
  try {
    await sessionService.createSession({
      tutorId: tutorId.value!,
      tutorSubjectId: slotForm.value.tutorSubjectId,
      startTime,
      endTime,
      status: 'available',
      durationMins,
    })
    slotForm.value = { tutorSubjectId: '', date: '', startTime: '', endTime: '' }
    showCreateSlot.value = false
  } catch (err: any) {
    slotError.value = err?.response?.data?.error || 'Failed to create session slot'
  } finally {
    slotCreating.value = false
  }
}
const tutorId = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  console.log(metadata)
  return typeof metadata?.tutorId === 'string' ? metadata.tutorId : null
})
const { tutor, searchForTutor, loading } = findTutorById()

watch(tutorId, (id) => {
  if (id) {
    searchForTutor(id)
  }
}, { immediate: true })

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
  { value: tutor.value?.averageRating?.toFixed(1) ?? '0.0', label: 'Average Rating', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { value: tutor.value?.totalReviews ?? '0', label: 'Total Reviews', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
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
        <div class="flex gap-4">
          <button @click="showCreateMeeting=!showCreateMeeting; showCreateSlot=false" class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90" style="background-color:#4A90D9">Create Google Meeting</button>
          <button @click="showCreateSlot=!showCreateSlot; showCreateMeeting=false" class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90" style="background-color:#2EAA4F">+ Create Session Slot</button>
        </div>
      </div>

      <!-- Create Google Meeting Form -->
      <div v-if="showCreateMeeting" class="rounded-2xl border p-6 mb-8" style="background-color:#fff;border-color:#E8F0FE">
        <h3 class="text-lg font-bold mb-4" style="color:#1B3A5C">Create Google Meeting</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Title</label>
            <input v-model="meetingForm.summary" type="text" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C" placeholder="e.g. Math Tutoring Session"/>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Date</label>
            <input v-model="meetingForm.date" type="date" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Start Time (UTC)</label>
            <input v-model="meetingForm.startTime" type="time" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">End Time (UTC)</label>
            <input v-model="meetingForm.endTime" type="time" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
        </div>
        <div class="mb-4">
          <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Description (Optional)</label>
          <textarea v-model="meetingForm.description" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C" rows="2"></textarea>
        </div>
        
        <div v-if="meetingError" class="mb-4 p-3 rounded-lg bg-red-50 text-red-600 text-xs">
          {{ meetingError }}
        </div>

        <div v-if="meetingResult" class="mb-4 p-4 rounded-xl bg-blue-50 border border-blue-100">
          <p class="text-sm font-bold text-blue-800 mb-2">Meeting Created!</p>
          <a :href="meetingResult.hangoutLink" target="_blank" class="text-xs text-blue-600 underline font-medium">Join Meeting: {{ meetingResult.hangoutLink }}</a>
        </div>

        <div class="flex items-center gap-3">
          <button @click="handleCreateMeeting" :disabled="meetingLoading" class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-50" style="background-color:#4A90D9">
            {{ meetingLoading ? 'Creating...' : 'Create Meeting' }}
          </button>
          <button @click="showCreateMeeting=false" class="px-6 py-2.5 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">Cancel</button>
        </div>
      </div>
      <div v-if="showCreateSlot" class="rounded-2xl border p-6 mb-8" style="background-color:#fff;border-color:#E8F0FE">
        <h3 class="text-lg font-bold mb-4" style="color:#1B3A5C">New Session Slot</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Subject</label>
            <select v-model="slotForm.tutorSubjectId" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C">
              <option value="" disabled>Select subject</option>
              <option v-for="s in tutor?.subjects" :key="s.tutorSubjectId" :value="s.tutorSubjectId">
                {{ s.subject }} ({{ s.academicLevel }})
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Date</label>
            <input v-model="slotForm.date" type="date" class="w-full px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color:#1B3A5C">Time</label>
            <div class="flex items-center gap-2">
              <input v-model="slotForm.startTime" type="time" class="flex-1 px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
              <span class="text-xs" style="color:#1B3A5C;opacity:0.5">to</span>
              <input v-model="slotForm.endTime" type="time" class="flex-1 px-4 py-2.5 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
            </div>
          </div>
        </div>
        <p v-if="slotError" class="mt-3 text-xs" style="color:#E74C3C">{{ slotError }}</p>
        <div class="flex items-center gap-3 mt-4">
          <button @click="handleCreateSlot" :disabled="slotCreating" class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-50" style="background-color:#2EAA4F">
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
