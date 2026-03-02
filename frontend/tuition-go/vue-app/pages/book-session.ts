// @ts-ignore
import { defineComponent, ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { mockSessions } from '../composables/useMockData'

function fmtDate(d: string) { return new Date(d).toLocaleDateString('en-SG', { weekday:'short', day:'numeric', month:'short', year:'numeric' }) }

export const BookSessionPage = defineComponent({
  name: 'BookSessionPage',
  components: { RouterLink },
  setup() {
    const route = useRoute()
    const confirmed = ref(false)
    const session = computed(() => mockSessions.find(s => s.id === route.params.sessionId))
    function confirmBooking() { confirmed.value = true }
    return { session, confirmed, confirmBooking, fmtDate }
  },
  template: `
    <div class="py-8 md:py-12" style="background-color:#F5F7FA">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <router-link to="/tutors" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9"><svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>Back</router-link>
        <div v-if="session&&!confirmed" class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">
          <div class="p-6 border-b" style="border-color:#E8F0FE;background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)"><h1 class="text-2xl font-extrabold text-white">Confirm Your Booking</h1><p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">Review the session details before confirming</p></div>
          <div class="p-6 space-y-6">
            <div class="flex items-center gap-4 p-4 rounded-xl" style="background-color:#F5F7FA"><img :src="session.tutorAvatar" :alt="session.tutorName" class="w-14 h-14 rounded-xl" crossorigin="anonymous" style="background-color:#E8F0FE"/><div><p class="font-bold" style="color:#1B3A5C">{{ session.tutorName }}</p><p class="text-sm" style="color:#4A90D9">{{ session.subject }} ({{ session.level }})</p></div></div>
            <div class="space-y-4">
              <div class="flex items-center justify-between py-3 border-b" style="border-color:#E8F0FE"><span class="text-sm" style="color:#1B3A5C;opacity:0.7">Date</span><span class="text-sm font-semibold" style="color:#1B3A5C">{{ fmtDate(session.date) }}</span></div>
              <div class="flex items-center justify-between py-3 border-b" style="border-color:#E8F0FE"><span class="text-sm" style="color:#1B3A5C;opacity:0.7">Time</span><span class="text-sm font-semibold" style="color:#1B3A5C">{{ session.startTime }} - {{ session.endTime }}</span></div>
              <div class="flex items-center justify-between py-3 border-b" style="border-color:#E8F0FE"><span class="text-sm" style="color:#1B3A5C;opacity:0.7">Duration</span><span class="text-sm font-semibold" style="color:#1B3A5C">{{ session.duration }} minutes</span></div>
              <div class="flex items-center justify-between py-3"><span class="text-sm font-bold" style="color:#1B3A5C">Total</span><span class="text-2xl font-extrabold" style="color:#2EAA4F">\${{ session.price.toFixed(2) }}</span></div>
            </div>
            <div class="rounded-xl p-5 border" style="border-color:#E8F0FE"><h3 class="text-sm font-bold mb-3" style="color:#1B3A5C">Payment Method</h3><div class="p-4 rounded-xl text-center" style="background-color:#F5F7FA;border:2px dashed #E8F0FE"><p class="text-xs font-medium" style="color:#1B3A5C;opacity:0.6">Stripe Checkout integration</p><p class="text-xs mt-1" style="color:#4A90D9">Secure payment processing</p></div></div>
            <button @click="confirmBooking" class="w-full py-4 rounded-xl text-base font-bold text-white hover:opacity-90 shadow-md" style="background-color:#2EAA4F">Confirm & Pay \${{ session.price.toFixed(2) }}</button>
          </div>
        </div>
        <div v-if="confirmed" class="rounded-2xl border p-8 text-center" style="background-color:#fff;border-color:#E8F0FE">
          <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style="background-color:rgba(46,170,79,0.1)"><svg class="w-10 h-10" style="color:#2EAA4F" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg></div>
          <h2 class="text-2xl font-extrabold mb-2" style="color:#1B3A5C">Booking Confirmed!</h2>
          <p class="text-sm mb-6" style="color:#1B3A5C;opacity:0.7">Your session has been booked. A Google Meet link has been sent to your email.</p>
          <div v-if="session" class="rounded-xl p-5 mb-6 text-left" style="background-color:#F5F7FA">
            <div class="space-y-3"><div class="flex justify-between text-sm"><span style="color:#1B3A5C;opacity:0.7">Tutor</span><span class="font-semibold" style="color:#1B3A5C">{{ session.tutorName }}</span></div><div class="flex justify-between text-sm"><span style="color:#1B3A5C;opacity:0.7">Subject</span><span class="font-semibold" style="color:#1B3A5C">{{ session.subject }}</span></div><div class="flex justify-between text-sm"><span style="color:#1B3A5C;opacity:0.7">Meeting Link</span><a href="https://meet.google.com/abc-defg-hij" target="_blank" class="font-semibold underline" style="color:#4A90D9">Join Google Meet</a></div></div>
          </div>
          <div class="flex flex-col sm:flex-row gap-3 justify-center"><router-link to="/dashboard" class="px-6 py-3 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Go to Dashboard</router-link><router-link to="/tutors" class="px-6 py-3 rounded-xl text-sm font-semibold border" style="border-color:#E8F0FE;color:#1B3A5C">Browse More Tutors</router-link></div>
        </div>
        <div v-if="!session" class="text-center py-20"><h2 class="text-2xl font-bold" style="color:#1B3A5C">Session not found</h2><router-link to="/tutors" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Browse Tutors</router-link></div>
      </div>
    </div>
  `,
})
