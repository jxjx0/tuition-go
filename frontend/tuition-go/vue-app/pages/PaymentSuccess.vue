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
  session_id: string
  student_email: string
} | null>(null)

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
  <section class="mx-auto max-w-4xl px-6 py-24">

    <!-- Steps (shown during loading and on success) -->
    <div v-if="loading || booking" class="mx-auto max-w-md mb-10">
      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wide">Booking Flow</h3>
        <div v-for="(step, i) in steps" :key="i" class="flex items-center gap-3">
          <!-- Icon -->
          <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
            :class="{
              'bg-emerald-100': step.status === 'done',
              'bg-blue-100':    step.status === 'loading',
              'bg-red-100':     step.status === 'error',
              'bg-slate-100':   step.status === 'waiting',
            }">
            <svg v-if="step.status === 'done'" class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            <svg v-else-if="step.status === 'loading'" class="animate-spin w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <svg v-else-if="step.status === 'error'" class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            <span v-else class="w-2 h-2 rounded-full bg-slate-300 mx-auto block"/>
          </div>
          <!-- Label -->
          <span class="text-sm"
            :class="{
              'text-emerald-700 font-semibold': step.status === 'done',
              'text-blue-600 font-semibold':    step.status === 'loading',
              'text-red-600 font-semibold':     step.status === 'error',
              'text-slate-400':                 step.status === 'waiting',
            }">
            {{ step.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-10 gap-3">
      <p class="text-slate-500 text-sm">Processing your booking...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-red-50 p-6 shadow-xl">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500 text-xl font-bold text-white">✕</div>
      <div>
        <h1 class="text-2xl font-bold text-red-900">Something went wrong</h1>
        <p class="text-red-700">{{ error }}</p>
      </div>
    </div>

    <!-- Success -->
    <div v-else-if="booking">
      <div class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-emerald-50 p-6 shadow-xl">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500 text-xl font-bold text-white">✓</div>
        <div>
          <h1 class="text-2xl font-bold text-emerald-900">Payment Verified & Booking Confirmed!</h1>
          <p class="text-emerald-800">process-booking called successfully.</p>
        </div>
      </div>

      <!-- Booking Details -->
      <div class="mt-10 rounded-2xl bg-white p-8 shadow-lg space-y-4">
        <h2 class="text-xl font-bold text-slate-900">Booking Details</h2>
        <div class="divide-y divide-slate-100 text-sm">
          <div class="flex justify-between py-3">
            <span class="text-slate-500">Session ID</span>
            <span class="font-mono font-semibold text-slate-800">{{ booking.session_id }}</span>
          </div>
          <div class="flex justify-between py-3">
            <span class="text-slate-500">Student Email</span>
            <span class="font-semibold text-slate-800">{{ booking.student_email }}</span>
          </div>
        </div>
      </div>

      <div class="mt-8 text-center">
        <RouterLink to="/dashboard" class="inline-block rounded-xl bg-emerald-500 px-8 py-4 font-semibold text-white transition hover:bg-emerald-600">
          Go to Dashboard
        </RouterLink>
      </div>
    </div>

    <!-- OLD UI (kept for reference) -->
    <!--
    <div class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-emerald-50 p-6 shadow-xl">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500 text-xl font-bold text-white">✓</div>
      <div>
        <h1 class="text-2xl font-bold text-emerald-900">Payment Successful!</h1>
        <p class="text-emerald-800">Your booking has been confirmed.</p>
      </div>
    </div>

    <div class="mt-12 grid gap-12 md:grid-cols-2">
      <div class="space-y-6 rounded-2xl bg-white p-8 shadow-lg">
        <h2 class="text-2xl font-bold text-slate-900">Payment Summary</h2>
        <div class="divide-y divide-slate-200">
          <div class="flex justify-between py-4">
            <span class="text-lg font-semibold text-slate-900">Trial Lesson</span>
            <span class="text-2xl font-bold text-slate-900">SGD 30.00</span>
          </div>
          <div class="flex justify-between py-4 text-sm text-slate-600">
            <span>Tutor: Mr. James Tan</span>
            <span>Secondary Math</span>
          </div>
          <div class="flex justify-between py-4 text-sm text-slate-600">
            <span>Date: 29 March 2026, 10:00 AM</span>
            <span>Booking #123</span>
          </div>
        </div>
        <div class="rounded-xl bg-slate-50 p-4 text-center">
          <p class="text-sm font-semibold text-slate-700">
            Paid via Stripe • Transaction ID: <span class="font-mono">sess_xxx</span>
          </p>
        </div>
      </div>

      <div class="space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h3 class="text-xl font-bold text-slate-900">What's next?</h3>
        <ol class="space-y-4">
          <li class="flex items-start gap-3 rounded-lg border-l-4 border-emerald-500 bg-slate-50 p-4 pl-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-bold">1</span>
            <div>
              <p class="font-semibold text-slate-900">Check your email</p>
              <p class="text-sm text-slate-600 mt-1">Lesson details and Zoom link sent to student@example.com</p>
            </div>
          </li>
          <li class="flex items-start gap-3 rounded-lg border-l-4 border-blue-500 bg-slate-50 p-4 pl-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-bold">2</span>
            <div>
              <p class="font-semibold text-slate-900">Join your lesson</p>
              <p class="text-sm text-slate-600 mt-1">Click the Zoom link at lesson time</p>
            </div>
          </li>
          <li class="flex items-start gap-3 rounded-lg border-l-4 border-indigo-500 bg-slate-50 p-4 pl-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold">3</span>
            <div>
              <p class="font-semibold text-slate-900">Rate your lesson</p>
              <p class="text-sm text-slate-600 mt-1">Share feedback after class to help other students</p>
            </div>
          </li>
        </ol>
      </div>
    </div>

    <div class="mt-16 rounded-2xl bg-slate-900 p-8 text-white text-center">
      <h3 class="text-2xl font-bold">Ready for your next lesson?</h3>
      <p class="mt-2 text-slate-300">Your tutor was great? Book more lessons with the same flow.</p>
      <RouterLink to="/tutors" class="mt-6 inline-block rounded-xl bg-emerald-500 px-8 py-4 font-semibold text-white transition hover:bg-emerald-600">
        Find More Tutors
      </RouterLink>
    </div>
    -->

  </section>
</template>

<style scoped>
/* Optional: Custom animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

section > * {
  animation: slideIn 0.5s ease-out forwards;
}
</style>
