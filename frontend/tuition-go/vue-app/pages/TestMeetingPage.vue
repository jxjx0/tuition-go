<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMeeting } from '../composables/useMeeting'
import axios from 'axios'

const { loading, error, result, createMeeting } = useMeeting()

const authRequired = ref(false)
const authUrl = ref('')

const form = ref({
  summary: 'Debug Meeting',
  description: 'Testing without Clerk',
  date: new Date().toISOString().split('T')[0],
  startTime: '10:00',
  endTime: '11:00'
})

async function checkAuthStatus() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/calendar/auth-status')
    if (response.data && response.data.authenticated === false) {
      fetchAuthUrl()
    }
  } catch (err) {
    console.error('Failed to check auth status:', err)
  }
}

async function fetchAuthUrl() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/calendar/auth-url')
    if (response.data && response.data.authUrl) {
      authUrl.value = response.data.authUrl
      authRequired.value = true
    }
  } catch (err) {
    console.error('Failed to fetch auth URL:', err)
  }
}

async function handleTest() {
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    const start = `${form.value.date}T${form.value.startTime}:00`
    const end = `${form.value.date}T${form.value.endTime}:00`
    
    await createMeeting({
      summary: form.value.summary,
      description: form.value.description,
      start_time: start,
      end_time: end,
      timezone: tz,
      attendees: []
    })
  } catch (err: any) {
    console.error('Test failed:', err)
    // Check if the error is 401 and includes an authUrl
    if (err.response?.status === 401 && err.response?.data?.authUrl) {
      authUrl.value = err.response.data.authUrl
      authRequired.value = true
    }
  }
}

onMounted(() => {
  checkAuthStatus()
})
</script>

<template>
  <div class="min-h-screen p-8 bg-gray-50 font-sans">
    <div class="max-w-xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-2xl font-bold text-gray-800">Clerk-Free Meeting Test</h1>
        <div v-if="!authRequired" class="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded uppercase">Google Authed</div>
      </div>
      <p class="text-sm text-gray-500 mb-8">This page bypasses login to test the Google Calendar integration.</p>

      <div class="space-y-4">
        <!-- Auth Alert -->
        <div v-if="authRequired" class="p-4 bg-amber-50 border border-amber-100 rounded-xl mb-6">
          <div class="flex items-start gap-3">
            <span class="text-lg">🔐</span>
            <div>
              <p class="text-amber-800 font-bold text-sm mb-1">Google Authentication Required</p>
              <p class="text-amber-700 text-xs mb-3">Your backend needs a one-time sign-in to create meetings.</p>
              <a 
                :href="authUrl" 
                target="_blank" 
                @click="authRequired = false"
                class="inline-block px-4 py-2 bg-amber-600 text-white text-xs font-bold rounded-lg hover:bg-amber-700 transition-colors"
              >
                Sign in with Google
              </a>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Meeting Title</label>
          <input v-model="form.summary" type="text" class="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"/>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Date</label>
            <input v-model="form.date" type="date" class="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Start Time</label>
            <input v-model="form.startTime" type="time" class="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"/>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-400 uppercase mb-1">End Time</label>
          <input v-model="form.endTime" type="time" class="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"/>
        </div>

        <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-xl text-sm font-medium">
          ❌ {{ error }}
        </div>

        <div v-if="result" class="p-4 bg-green-50 border border-green-100 rounded-xl">
          <p class="text-green-800 font-bold mb-1">Meeting Created!</p>
          <a :href="result.hangoutLink" target="_blank" class="text-blue-600 underline text-sm break-all">{{ result.hangoutLink }}</a>
        </div>

        <button 
          @click="handleTest" 
          :disabled="loading || authRequired"
          class="w-full py-4 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-lg shadow-blue-100 mt-4"
        >
          {{ loading ? 'Creating Meeting...' : 'Trigger Calendar API' }}
        </button>
      </div>
      
      <div class="mt-8 pt-6 border-t border-gray-50 flex items-center justify-between text-[10px] text-gray-300 uppercase tracking-widest font-bold">
        <span>Layer 4 Integrated</span>
        <span>Bypassing Layer 1 Auth</span>
      </div>
    </div>
  </div>
</template>
