// @ts-ignore
import { defineComponent, ref, computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { mockSessions } from '../composables/useMockData'

function fmtDate(d: string) { return new Date(d).toLocaleDateString('en-SG', { weekday:'short', day:'numeric', month:'short', year:'numeric' }) }

export const SessionDetailPage = defineComponent({
  name: 'SessionDetailPage',
  components: { RouterLink },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const showCancel = ref(false)
    const session = computed(() => mockSessions.find(s => s.id === route.params.id))
    const statusLabel = computed(() => { if (!session.value) return ''; const m: Record<string,string> = { booked:'Upcoming', completed:'Completed', cancelled:'Cancelled', available:'Available' }; return m[session.value.status] || session.value.status })
    const headerStyle = computed(() => { if (!session.value) return ''; if (session.value.status==='completed') return 'background:linear-gradient(135deg,#1a6b36 0%,#2EAA4F 100%)'; if (session.value.status==='cancelled') return 'background:linear-gradient(135deg,#991b1b 0%,#ef4444 100%)'; return 'background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)' })
    function cancelSession() { showCancel.value = false; router.push('/dashboard') }
    return { session, showCancel, statusLabel, headerStyle, cancelSession, fmtDate }
  },
  template: `
    <div class="py-8 md:py-12" style="background-color:#F5F7FA">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9"><svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>Back to Dashboard</router-link>
        <div v-if="session" class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">
          <div class="p-6" :style="headerStyle">
            <span class="px-3 py-1 rounded-full text-xs font-bold mb-3 inline-block" style="background-color:rgba(255,255,255,0.2);color:#fff">{{ statusLabel }}</span>
            <h1 class="text-2xl font-extrabold text-white">{{ session.subject }} ({{ session.level }})</h1>
            <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">Session with {{ session.tutorName }}</p>
          </div>
          <div class="p-6 space-y-6">
            <div class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA">
              <img :src="session.tutorAvatar" :alt="session.tutorName" class="w-14 h-14 rounded-xl" crossorigin="anonymous" style="background-color:#E8F0FE"/><div class="flex-1"><p class="font-bold" style="color:#1B3A5C">{{ session.tutorName }}</p><router-link :to="'/tutors/'+session.tutorId" class="text-xs font-medium hover:underline" style="color:#4A90D9">View Profile</router-link></div>
              <p class="text-xl font-extrabold" style="color:#2EAA4F">\${{ session.price.toFixed(2) }}</p>
            </div>
            <div class="space-y-4">
              <div class="flex items-center justify-between py-3 border-b" style="border-color:#E8F0FE"><span class="text-sm" style="color:#1B3A5C;opacity:0.7">Date</span><span class="text-sm font-semibold" style="color:#1B3A5C">{{ fmtDate(session.date) }}</span></div>
              <div class="flex items-center justify-between py-3 border-b" style="border-color:#E8F0FE"><span class="text-sm" style="color:#1B3A5C;opacity:0.7">Time</span><span class="text-sm font-semibold" style="color:#1B3A5C">{{ session.startTime }} - {{ session.endTime }} ({{ session.duration }} min)</span></div>
            </div>
            <div v-if="session.notes" class="p-4 rounded-xl" style="background-color:#F5F7FA"><p class="text-xs font-semibold mb-1" style="color:#1B3A5C">Session Notes</p><p class="text-sm" style="color:#1B3A5C;opacity:0.8">{{ session.notes }}</p></div>
            <div v-if="session.meetingLink&&session.status==='booked'" class="p-4 rounded-xl border" style="border-color:#E8F0FE"><p class="text-xs font-semibold mb-2" style="color:#1B3A5C">Google Meet</p><a :href="session.meetingLink" target="_blank" class="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90" style="background-color:#2EAA4F"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>Join Meeting</a></div>
            <div class="flex flex-col sm:flex-row gap-3">
              <button v-if="session.status==='booked'&&!showCancel" @click="showCancel=true" class="flex-1 py-3 rounded-xl text-sm font-semibold border hover:bg-red-50" style="border-color:#ef4444;color:#ef4444">Cancel Session</button>
              <router-link v-if="session.status==='completed'" :to="'/review/'+session.id" class="flex-1 py-3 rounded-xl text-sm font-semibold text-white text-center hover:opacity-90" style="background-color:#4A90D9">Leave a Review</router-link>
            </div>
            <div v-if="showCancel" class="p-5 rounded-xl border" style="border-color:#ef4444;background-color:rgba(239,68,68,0.03)">
              <p class="text-sm font-bold mb-1" style="color:#ef4444">Cancel this session?</p>
              <p class="text-xs mb-4" style="color:#1B3A5C;opacity:0.7">A full refund will be processed within 3-5 business days.</p>
              <div class="flex gap-3"><button @click="cancelSession" class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white" style="background-color:#ef4444">Yes, Cancel</button><button @click="showCancel=false" class="px-6 py-2.5 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">Keep Session</button></div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-20"><h2 class="text-2xl font-bold" style="color:#1B3A5C">Session not found</h2><router-link to="/dashboard" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link></div>
      </div>
    </div>
  `,
})
