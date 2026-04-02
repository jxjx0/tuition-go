<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'
import { useSessionService } from '../services/sessionService'
import { findTutorById } from '../composables/useTutors'

const route = useRoute()
const router = useRouter()
const { user } = useUser()
const sessionService = useSessionService()
const { tutor, searchForTutor } = findTutorById()

const sessionId = route.params.sessionId as string

function toUtcDate(d: string) {
  return new Date(d + 'Z')
}

function fmtDate(d: string) {
  return toUtcDate(d).toLocaleDateString('en-SG', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
}

function fmtTime(d: string) {
  return toUtcDate(d).toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

const session = ref<any>(null)
const loading = ref(true)
const saving = ref(false)
const deleting = ref(false)
const completing = ref(false)
const error = ref('')
const saveError = ref('')
const showDeleteConfirm = ref(false)
const saved = ref(false)
const isEditing = ref(false)
const justCompleted = ref(false)

const tutorId = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  return typeof metadata?.tutorId === 'string' ? metadata.tutorId : null
})

const isOwner = computed(() => session.value && tutorId.value === session.value.tutorId)
const isEditable = computed(() => session.value?.status === 'available')
const isCompleted = computed(() => session.value?.status === 'completed')
const isBooked = computed(() => session.value?.status === 'booked')
const isCompletable = computed(() => {
  if (!isBooked.value) return false
  const endTime = session.value?.endTime
  if (!endTime) return false
  return new Date() > new Date(endTime + 'Z')
})

const form = ref({ tutorSubjectId: '', date: '', startTime: '', endTime: '' })

watch(tutorId, (id) => { if (id) searchForTutor(id) }, { immediate: true })

onMounted(async () => {
  try {
    const { data } = await sessionService.getSessionById(sessionId)
    session.value = data
    populateForm(data)
  } catch {
    error.value = 'Failed to load session.'
  } finally {
    loading.value = false
  }
})

function populateForm(data: any) {
  const start = toUtcDate(data.startTime)
  const end = toUtcDate(data.endTime)
  form.value = {
    tutorSubjectId: data.tutorSubjectId,
    date: start.toISOString().slice(0, 10),
    startTime: start.toISOString().slice(11, 16),
    endTime: end.toISOString().slice(11, 16),
  }
}

function cancelEdit() {
  populateForm(session.value)
  saveError.value = ''
  isEditing.value = false
}

async function saveSession() {
  saveError.value = ''
  const startTime = `${form.value.date}T${form.value.startTime}:00`
  const endTime = `${form.value.date}T${form.value.endTime}:00`
  const durationMins = (new Date(endTime).getTime() - new Date(startTime).getTime()) / 60000
  if (durationMins <= 0) {
    saveError.value = 'End time must be after start time'
    return
  }
  saving.value = true
  try {
    const selectedSubject = tutor.value?.subjects?.find((s: any) => s.tutorSubjectId === form.value.tutorSubjectId)
    const summary = selectedSubject ? `${selectedSubject.subject} (${selectedSubject.academicLevel})` : 'Tutor Session'
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone

    await sessionService.updateSessionWithCalendar(sessionId, {
      tutorSubjectId: form.value.tutorSubjectId,
      startTime,
      endTime,
      durationMins,
      summary,
      timezone: tz,
    })
    const { data: refreshed } = await sessionService.getSessionById(sessionId)
    session.value = refreshed
    populateForm(refreshed)
    isEditing.value = false
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (err: any) {
    saveError.value = err?.response?.data?.message || err?.response?.data?.error || 'Failed to save session'
  } finally {
    saving.value = false
  }
}

async function completeSession() {
  completing.value = true
  saveError.value = ''
  try {
    await sessionService.completeSession(sessionId, tutorId.value!)
    const { data: refreshed } = await sessionService.getSessionById(sessionId)
    session.value = refreshed
    justCompleted.value = true
    setTimeout(() => { justCompleted.value = false }, 4000)
  } catch (err: any) {
    saveError.value = err?.response?.data?.message || 'Failed to mark session as complete'
  } finally {
    completing.value = false
  }
}

async function deleteSession() {
  deleting.value = true
  try {
    await sessionService.deleteSession(sessionId)
    router.push('/tutor-dashboard')
  } catch (err: any) {
    saveError.value = err?.response?.data?.error || 'Failed to delete session'
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">

      <router-link to="/tutor-dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9">
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
      <div v-else-if="error" class="text-center py-20 text-sm" style="color:#E74C3C">{{ error }}</div>
      <div v-else-if="!isOwner" class="text-center py-20">
        <p class="text-sm font-semibold" style="color:#E74C3C">You are not authorised to view this session.</p>
      </div>

      <template v-else>

        <!-- ===== COMPLETED VIEW ===== -->
        <div v-if="isCompleted" class="space-y-5">

          <!-- Just completed banner -->
          <div v-if="justCompleted" class="flex items-center gap-3 p-4 rounded-2xl text-sm font-semibold" style="background-color:rgba(46,170,79,0.1);color:#2EAA4F;border:1px solid rgba(46,170,79,0.2)">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Session marked as complete!
          </div>

          <!-- Header card -->
          <div class="rounded-2xl overflow-hidden" style="background-color:#fff;border:1px solid #E8F0FE">
            <div class="p-6 flex items-center gap-4" style="background:linear-gradient(135deg,#1a7a3a 0%,#2EAA4F 100%)">
              <div class="h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color:rgba(255,255,255,0.2)">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <h1 class="text-xl font-extrabold text-white">Session Completed</h1>
                <p class="text-sm mt-0.5" style="color:rgba(255,255,255,0.75)">{{ session.subjectName }} · {{ session.academicLevel }}</p>
              </div>
              <span class="ml-auto px-3 py-1 rounded-full text-xs font-semibold" style="background-color:rgba(255,255,255,0.2);color:#fff">Completed</span>
            </div>

            <!-- Session details -->
            <div class="p-6 space-y-5">
              <!-- Date & Time -->
              <div class="rounded-xl p-4 space-y-3" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color:#E8F0FE">
                    <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Date</p>
                    <p class="text-sm font-bold" style="color:#1B3A5C">{{ fmtDate(session.startTime) }}</p>
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

              <!-- Subject & earnings -->
              <div class="grid grid-cols-2 gap-5">
                <div>
                  <p class="text-xs font-semibold uppercase mb-1" style="color:#1B3A5C;opacity:0.4">Subject</p>
                  <p class="text-sm font-semibold" style="color:#1B3A5C">{{ session.subjectName }} ({{ session.academicLevel }})</p>
                </div>
                <div v-if="session.totalPrice">
                  <p class="text-xs font-semibold uppercase mb-1" style="color:#1B3A5C;opacity:0.4">Earnings</p>
                  <p class="text-sm font-bold" style="color:#2EAA4F">${{ session.totalPrice.toFixed(2) }}</p>
                </div>
              </div>

              <!-- Student -->
              <div v-if="session.studentName" class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
                <img
                  :src="session.studentImageUrl || 'https://api.dicebear.com/9.x/notionists/svg?seed=' + session.studentId"
                  class="w-12 h-12 rounded-xl object-cover flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"
                />
                <div>
                  <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Student</p>
                  <p class="text-sm font-bold" style="color:#1B3A5C">{{ session.studentName }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Review section -->
          <div class="rounded-2xl p-6" style="background-color:#fff;border:1px solid #E8F0FE">
            <h3 class="text-sm font-bold mb-4" style="color:#1B3A5C">Student Review</h3>
            <!-- Placeholder until review atomic is built -->
            <div class="flex flex-col items-center gap-2 py-6 rounded-xl" style="background-color:#F5F7FA">
              <svg class="w-8 h-8" style="color:#1B3A5C;opacity:0.2" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.562.562 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z"/>
              </svg>
              <p class="text-xs font-medium" style="color:#1B3A5C;opacity:0.4">No review yet</p>
              <p class="text-xs" style="color:#1B3A5C;opacity:0.3">The student hasn't left a review for this session</p>
            </div>
          </div>

        </div>

        <!-- ===== NORMAL (available / booked) VIEW ===== -->
        <div v-else class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">

          <!-- Header -->
          <div class="p-6 flex items-start justify-between" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
            <div>
              <h1 class="text-2xl font-extrabold text-white">Session Details</h1>
              <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">{{ session.subjectName }} · {{ session.academicLevel }}</p>
            </div>
            <span class="px-3 py-1 rounded-full text-xs font-semibold mt-1" :style="session.status === 'available' ? 'background-color:rgba(46,170,79,0.2);color:#fff' : 'background-color:rgba(255,255,255,0.2);color:#fff'">
              {{ session.status === 'available' ? 'Available' : 'Booked' }}
            </span>
          </div>

          <!-- Details view -->
          <div v-if="!isEditing" class="p-6 space-y-5">
            <!-- Date & Time card -->
            <div class="rounded-xl p-4 space-y-3" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color:#E8F0FE">
                  <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                </div>
                <div>
                  <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Date</p>
                  <p class="text-sm font-bold" style="color:#1B3A5C">{{ fmtDate(session.startTime) }}</p>
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
                    {{ fmtTime(session.startTime) }}
                    –
                    {{ fmtTime(session.endTime) }}
                    <span class="font-normal" style="color:#1B3A5C;opacity:0.5">· {{ session.durationMins }} mins</span>
                  </p>
                </div>
              </div>
            </div>

            <!-- Subject & Price -->
            <div class="grid grid-cols-2 gap-5">
              <div>
                <p class="text-xs font-semibold uppercase mb-1" style="color:#1B3A5C;opacity:0.4">Subject</p>
                <p class="text-sm font-semibold" style="color:#1B3A5C">{{ session.subjectName }} ({{ session.academicLevel }})</p>
              </div>
              <div v-if="session.totalPrice">
                <p class="text-xs font-semibold uppercase mb-1" style="color:#1B3A5C;opacity:0.4">Total Price</p>
                <p class="text-sm font-bold" style="color:#2EAA4F">${{ session.totalPrice.toFixed(2) }}</p>
              </div>
            </div>

            <!-- Student details for booked sessions -->
            <div v-if="session.studentName" class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
              <img
                :src="session.studentImageUrl || 'https://api.dicebear.com/9.x/notionists/svg?seed=' + session.studentId"
                class="w-12 h-12 rounded-xl object-cover flex-shrink-0" crossorigin="anonymous" style="background-color:#E8F0FE"
              />
              <div>
                <p class="text-xs font-semibold uppercase mb-0.5" style="color:#1B3A5C;opacity:0.4">Student</p>
                <p class="text-sm font-bold" style="color:#1B3A5C">{{ session.studentName }}</p>
              </div>
            </div>

            <!-- Meeting link for booked sessions -->
            <div v-if="isBooked && session.meetingLink" class="p-4 rounded-xl border" style="border-color:#E8F0FE">
              <p class="text-xs font-semibold mb-2" style="color:#1B3A5C">Google Meet</p>
              <a :href="session.meetingLink" target="_blank" class="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90" style="background-color:#2EAA4F">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                Join Meeting
              </a>
            </div>

            <!-- Booked warning + actions -->
            <div v-if="isBooked" class="space-y-4">
              <div class="p-4 rounded-xl text-sm font-medium" style="background-color:#FFF8E7;color:#B7791F;border:1px solid #F6E05E">
                This session has been booked and cannot be edited.
              </div>
              <p v-if="saveError" class="text-xs" style="color:#E74C3C">{{ saveError }}</p>
              <div class="flex justify-end items-center pt-2" style="border-top:1px solid #E8F0FE">
                <button
                  v-if="isCompletable"
                  @click="completeSession"
                  :disabled="completing"
                  class="px-6 py-2.5 rounded-xl text-sm font-bold text-white disabled:opacity-50 flex items-center gap-2"
                  style="background-color:#7C3AED"
                >
                  <svg v-if="completing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  {{ completing ? 'Saving...' : 'Mark as Complete' }}
                </button>
              </div>
            </div>

            <!-- Actions for available sessions -->
            <div v-if="isEditable" class="flex items-center justify-between pt-2" style="border-top:1px solid #E8F0FE">
              <button @click="showDeleteConfirm = true" class="px-5 py-2.5 rounded-xl text-sm font-semibold" style="background-color:rgba(231,76,60,0.08);color:#E74C3C">
                Delete
              </button>
              <button @click="isEditing = true" class="px-8 py-2.5 rounded-xl text-sm font-bold text-white" style="background-color:#4A90D9">
                Edit
              </button>
            </div>
          </div>

          <!-- Edit form -->
          <div v-else class="p-6 space-y-5">
            <div>
              <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Subject</label>
              <select v-model="form.tutorSubjectId" class="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" style="border-color:#E8F0FE;color:#1B3A5C">
                <option v-for="s in tutor?.subjects" :key="s.tutorSubjectId" :value="s.tutorSubjectId">
                  {{ s.subject }} ({{ s.academicLevel }})
                </option>
              </select>
            </div>
            <div>
              <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Date</label>
              <input v-model="form.date" type="date" class="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" style="border-color:#E8F0FE;color:#1B3A5C"/>
            </div>
            <div>
              <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Time</label>
              <div class="flex items-center gap-3">
                <input v-model="form.startTime" type="time" class="flex-1 px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" style="border-color:#E8F0FE;color:#1B3A5C"/>
                <span class="text-xs" style="color:#1B3A5C;opacity:0.5">to</span>
                <input v-model="form.endTime" type="time" class="flex-1 px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" style="border-color:#E8F0FE;color:#1B3A5C"/>
              </div>
            </div>

            <p v-if="saveError" class="text-xs" style="color:#E74C3C">{{ saveError }}</p>

            <div class="flex items-center justify-between pt-2" style="border-top:1px solid #E8F0FE">
              <button @click="cancelEdit" class="px-5 py-2.5 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">
                Cancel
              </button>
              <button @click="saveSession" :disabled="saving" class="px-8 py-2.5 rounded-xl text-sm font-bold text-white disabled:opacity-50 flex items-center gap-2" style="background-color:#4A90D9">
                <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>

        </div>

        <!-- Delete confirmation modal -->
        <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center z-50" style="background-color:rgba(0,0,0,0.4)">
          <div class="rounded-2xl p-6 max-w-sm w-full mx-4" style="background-color:#fff">
            <h3 class="text-base font-bold mb-2" style="color:#1B3A5C">Delete this session?</h3>
            <p class="text-sm mb-5" style="color:#1B3A5C;opacity:0.6">This action cannot be undone.</p>
            <div class="flex gap-3">
              <button @click="showDeleteConfirm = false" class="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">Cancel</button>
              <button @click="deleteSession" :disabled="deleting" class="flex-1 px-4 py-2.5 rounded-xl text-sm font-bold text-white disabled:opacity-50 flex items-center justify-center gap-2" style="background-color:#E74C3C">
                <svg v-if="deleting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ deleting ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Saved toast -->
        <div v-if="saved" class="fixed bottom-6 right-6 flex items-center gap-3 px-5 py-4 rounded-xl shadow-lg" style="background-color:#fff;border:1px solid #E8F0FE;z-index:50">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background-color:rgba(46,170,79,0.1)">
            <svg class="w-4 h-4" style="color:#2EAA4F" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <p class="text-sm font-bold" style="color:#1B3A5C">Session updated</p>
        </div>

      </template>
    </div>
  </div>
</template>
