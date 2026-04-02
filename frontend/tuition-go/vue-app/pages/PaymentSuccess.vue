<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";
import { onMounted, ref } from "vue";
import { useApi } from "../services/api";

const route = useRoute();
const api = useApi();

const stripeSessionId = route.query.stripe_session_id as string;

type StepStatus = 'waiting' | 'loading' | 'done' | 'error'

const steps = ref([
  { label: 'Stripe redirected with session ID', status: 'done' as StepStatus },
  { label: 'Confirming booking',                status: 'waiting' as StepStatus },
])

const loading = ref(true)
const error = ref<string | null>(null)
const booking = ref<{
  sessionId: string
  student_email: string
  student_name: string
  tutor_name: string
  amount_paid: number
  subject: string
  start_time: string
  end_time: string
  status: string
} | null>(null)

function fmtDate(d: string) {
  return new Date(d + 'Z').toLocaleDateString('en-SG', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
}

function fmtTime(d: string) {
  return new Date(d + 'Z').toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

function fmtAmount(cents: number) {
  return (cents / 100).toFixed(2)
}

onMounted(async () => {
  if (!stripeSessionId) {
    error.value = "No payment session found."
    loading.value = false
    return
  }
  try {
    steps.value[1].status = 'loading'
    const { data: bookingData } = await api.post("/process-booking/process-booking", {
      stripe_session_id: stripeSessionId,
    });
    steps.value[1].status = 'done'
    booking.value = bookingData
  } catch (err) {
    const failingStep = steps.value.find(s => s.status === 'loading')
    if (failingStep) failingStep.status = 'error'
    console.error("Booking process failed:", err);
    error.value = "Something went wrong confirming your booking."
  } finally {
    loading.value = false
  }
});
</script>

<template>
  <!-- Loading -->
  <div v-if="loading" class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
    <div class="flex flex-col items-center gap-6">
      <div class="relative">
        <div class="h-20 w-20 rounded-full border-4 border-slate-200"></div>
        <div class="absolute inset-0 h-20 w-20 rounded-full border-4 border-t-blue-500 animate-spin"></div>
      </div>
      <div class="text-center">
        <p class="text-slate-800 text-xl font-semibold">Confirming your booking</p>
        <p class="text-slate-500 text-sm mt-1">Please wait a moment…</p>
      </div>
    </div>
  </div>

  <!-- Error -->
  <div v-else-if="error" class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
    <div class="bg-white rounded-3xl shadow-xl p-10 max-w-md w-full text-center">
      <div class="mx-auto mb-6 h-16 w-16 rounded-full bg-red-100 flex items-center justify-center">
        <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-slate-900">Something went wrong</h1>
      <p class="mt-2 text-slate-500">{{ error }}</p>
      <RouterLink to="/" class="mt-8 inline-block rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-700 transition">
        Back to Home
      </RouterLink>
    </div>
  </div>

  <!-- Success -->
  <div v-else-if="booking" class="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-slate-50">
    <div class="mx-auto max-w-2xl px-6 py-16">

      <!-- Success badge -->
      <div class="flex flex-col items-center text-center mb-12 animate-fadeUp">
        <div class="relative mb-6">
          <div class="h-24 w-24 rounded-full bg-emerald-100 flex items-center justify-center shadow-lg shadow-emerald-100">
            <svg class="w-12 h-12 text-emerald-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div class="absolute -bottom-1 -right-1 h-7 w-7 rounded-full bg-emerald-500 flex items-center justify-center shadow-md">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-slate-900">Payment Successful</h1>
        <p class="mt-2 text-slate-500 text-base">Your lesson has been confirmed. See you there!</p>
      </div>

      <!-- Receipt card -->
      <div class="bg-white rounded-3xl shadow-xl overflow-hidden animate-fadeUp" style="animation-delay: 0.1s">

        <!-- Amount header -->
        <div class="px-8 py-6 flex items-center justify-between border-b border-slate-100">
          <div>
            <p class="text-slate-400 text-xs font-semibold uppercase tracking-widest">Amount Paid</p>
            <p class="text-emerald-600 text-4xl font-bold mt-1">SGD {{ fmtAmount(booking.amount_paid) }}</p>
          </div>
          <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center">
            <svg class="w-7 h-7 text-emerald-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z"/>
            </svg>
          </div>
        </div>

        <!-- Divider with label -->
        <div class="relative flex items-center px-8 py-3 bg-slate-50 border-y border-slate-100">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Booking Details</span>
        </div>

        <!-- Detail rows -->
        <div class="px-8 py-2 divide-y divide-slate-100">

          <!-- Subject -->
          <div class="flex items-center gap-4 py-4">
            <div class="flex-shrink-0 h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-400 font-medium">Subject</p>
              <p class="text-sm font-semibold text-slate-800 mt-0.5">{{ booking.subject }}</p>
            </div>
          </div>

          <!-- Tutor -->
          <div class="flex items-center gap-4 py-4">
            <div class="flex-shrink-0 h-10 w-10 rounded-xl bg-violet-50 flex items-center justify-center">
              <svg class="w-5 h-5 text-violet-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-400 font-medium">Tutor</p>
              <p class="text-sm font-semibold text-slate-800 mt-0.5">{{ booking.tutor_name }}</p>
            </div>
          </div>

          <!-- Date -->
          <div class="flex items-center gap-4 py-4">
            <div class="flex-shrink-0 h-10 w-10 rounded-xl bg-amber-50 flex items-center justify-center">
              <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-400 font-medium">Date</p>
              <p class="text-sm font-semibold text-slate-800 mt-0.5">{{ fmtDate(booking.start_time) }}</p>
            </div>
          </div>

          <!-- Time -->
          <div class="flex items-center gap-4 py-4">
            <div class="flex-shrink-0 h-10 w-10 rounded-xl bg-teal-50 flex items-center justify-center">
              <svg class="w-5 h-5 text-teal-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-slate-400 font-medium">Time</p>
              <p class="text-sm font-semibold text-slate-800 mt-0.5">{{ fmtTime(booking.start_time) }} – {{ fmtTime(booking.end_time) }}</p>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="px-8 py-5 bg-slate-50 border-t border-slate-100 flex items-center gap-2">
          <svg class="w-4 h-4 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <p class="text-xs text-slate-500">Confirmation sent to <span class="font-semibold text-slate-700">{{ booking.student_email }}</span></p>
        </div>
      </div>

      <!-- What's next -->
      <div class="mt-8 bg-white rounded-3xl shadow-sm border border-slate-100 px-8 py-6 animate-fadeUp" style="animation-delay: 0.2s">
        <h3 class="text-base font-bold text-slate-900 mb-5">What happens next?</h3>
        <ol class="space-y-4">
          <li class="flex items-start gap-4">
            <div class="flex-shrink-0 h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 text-sm font-bold">1</div>
            <div>
              <p class="text-sm font-semibold text-slate-800">Check your inbox</p>
              <p class="text-xs text-slate-500 mt-0.5">Lesson details and Google Meet link are on their way to your email</p>
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 text-sm font-bold">2</div>
            <div>
              <p class="text-sm font-semibold text-slate-800">Join your lesson</p>
              <p class="text-xs text-slate-500 mt-0.5">Click the Meet link at the scheduled time to start your session</p>
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="flex-shrink-0 h-8 w-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 text-sm font-bold">3</div>
            <div>
              <p class="text-sm font-semibold text-slate-800">Leave a review</p>
              <p class="text-xs text-slate-500 mt-0.5">Rate your tutor after the session to help other students</p>
            </div>
          </li>
        </ol>
      </div>

      <!-- CTA -->
      <div class="mt-8 flex flex-col sm:flex-row gap-3 justify-center animate-fadeUp" style="animation-delay: 0.3s">
        <RouterLink to="/dashboard" class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-8 py-3.5 font-semibold text-white hover:bg-emerald-600 transition shadow-lg shadow-emerald-100">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          Go to Dashboard
        </RouterLink>
        <RouterLink to="/tutors" class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-8 py-3.5 font-semibold text-slate-700 hover:bg-slate-50 transition">
          Browse More Tutors
        </RouterLink>
      </div>

    </div>
  </div>
</template>

<style scoped>
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeUp {
  animation: fadeUp 0.5s ease-out both;
}
</style>
