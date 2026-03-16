<script setup lang="ts">
import { ref } from 'vue'
import { useMeeting } from '../composables/useMeeting'

const { loading, error, result, createMeeting } = useMeeting()

const form = ref({
  summary: 'Debug Meeting',
  description: 'Testing without Clerk',
  date: new Date().toISOString().split('T')[0],
  startTime: '10:00',
  endTime: '11:00'
})

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
  } catch (err) {
    console.error('Test failed:', err)
  }
}
</script>

<template>
  <div class="min-h-screen p-8 bg-gray-50 font-sans">
    <div class="max-w-xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
      <h1 class="text-2xl font-bold text-gray-800 mb-2">Clerk-Free Meeting Test</h1>
      <p class="text-sm text-gray-500 mb-8">This page bypasses login to test the Google Calendar integration.</p>

      <div class="space-y-4">
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
          <p class="text-green-800 font-bold mb-1">Success!</p>
          <a :href="result.hangoutLink" target="_blank" class="text-blue-600 underline text-sm">{{ result.hangoutLink }}</a>
        </div>

        <button 
          @click="handleTest" 
          :disabled="loading"
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
