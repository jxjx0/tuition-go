<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ref, onMounted } from "vue";
import { useApi } from "../services/api";
import { usePaymentService } from "../services/paymentService";

const route = useRoute();
const router = useRouter();
const api = useApi();

interface Booking {
  studentId: string
  sessionId: string
  tutor_name: string
  amount_paid: number
  subject: string
  start_time: string
  end_time: string
  status: string
}

const booking = ref<Booking | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const { getStripeSession } = usePaymentService()


const startCheckout = async () => {
  if (!booking.value?.sessionId || !booking.value?.studentId) return
  console.log("Checking: ",booking.value.sessionId, booking.value.studentId)
  try {
    const { data } = await api.post('/checkout/checkout', {
      session_id: booking.value.sessionId,
      student_id: booking.value.studentId
    })

    // Redirect to Stripe hosted checkout page
    window.location.href = data.url

  } catch (err) {
    console.error('Failed to initiate checkout', err)
  }
}
function fmtDate(d: string) {
  return new Date(d + "Z").toLocaleDateString("en-SG", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

function fmtTime(d: string) {
  return new Date(d + "Z").toLocaleTimeString("en-SG", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

function fmtAmount(cents: number) {
  return (cents / 100).toFixed(2);
}

onMounted(async () => {
  const stripeSessionId = route.query.stripe_session_id as string
  console.log("Stripe Session ID from query:", stripeSessionId)

  try {
    if (!stripeSessionId) {
      error.value = "No payment session found"
      loading.value = false
      return
    }

    // Step 1: Get internal session_id from Stripe metadata
    const res = await getStripeSession(stripeSessionId)

    // Step 2: Use internal session_id to fetch your booking details
    const { data: bookingData } = await api.get(
      `/process-booking/booking-details/${stripeSessionId}`,
    )

    console.log("Booking details fetched:", bookingData)

    booking.value = {
      studentId: bookingData.studentId || "N/A",
      sessionId: bookingData.sessionId || "N/A",
      tutor_name: bookingData.tutor_name || "N/A",
      amount_paid: bookingData.amount_paid || 0,
      subject: bookingData.subject || "N/A",
      start_time: bookingData.start_time || "",
      end_time: bookingData.end_time || "",
      status: bookingData.status || "cancelled",
    }
  } catch (err) {
    console.error("Failed to fetch booking details:", err)
    error.value = "Failed to load booking details. Please try again."
  } finally {
    loading.value = false
  }
})

</script>

<template>
  <!-- Loading -->
  <div
    v-if="loading"
    class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center"
  >
    <div class="flex flex-col items-center gap-6">
      <div class="relative">
        <div class="h-20 w-20 rounded-full border-4 border-slate-200"></div>
        <div
          class="absolute inset-0 h-20 w-20 rounded-full border-4 border-t-yellow-500 animate-spin"
        ></div>
      </div>
      <div class="text-center">
        <p class="text-slate-800 text-xl font-semibold">
          Loading payment details
        </p>
        <p class="text-slate-500 text-sm mt-1">Please wait a moment…</p>
      </div>
    </div>
  </div>

  <!-- Error -->
  <div
    v-else-if="error"
    class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6"
  >
    <div
      class="bg-white rounded-3xl shadow-xl p-10 max-w-md w-full text-center"
    >
      <div
        class="mx-auto mb-6 h-16 w-16 rounded-full bg-red-100 flex items-center justify-center"
      >
        <svg
          class="w-8 h-8 text-red-500"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 18L18 6M6 6l12 12"
          ></path>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-slate-900">Something went wrong</h1>
      <p class="mt-2 text-slate-500">{{ error }}</p>
      <RouterLink
        to="/"
        class="mt-8 inline-block rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-700 transition"
      >
        Back to Home
      </RouterLink>
    </div>
  </div>

  <!-- Success Content -->
  <section v-else class="mx-auto max-w-4xl px-6 py-24">
    <!-- Failed Banner -->
    <div
      class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-yellow-50 p-6 shadow-xl border border-yellow-200"
    >
      <div
        class="flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-500 text-xl font-bold text-white"
      >
        !
      </div>
      <div>
        <h1 class="text-2xl font-bold text-yellow-900">
          Payment Not Completed
        </h1>
        <p class="text-yellow-800">Your booking is not confirmed yet.</p>
      </div>
    </div>

    <div class="mt-12 grid gap-12 md:grid-cols-2">
      <!-- Payment Summary -->
      <div
        class="space-y-6 rounded-2xl bg-white border border-slate-200 p-8 shadow-lg"
      >
        <h2 class="text-2xl font-bold text-slate-900">Payment Summary</h2>
        <div class="divide-y divide-slate-200">
          <div class="flex justify-between py-4">
            <span class="text-lg font-semibold text-slate-900"
              >Trial Lesson</span
            >
            <span
              class="text-2xl font-bold text-slate-900 line-through text-yellow-500"
              >SGD {{ fmtAmount(booking?.amount_paid || 0) }}</span
            >
          </div>
          <div class="flex justify-between py-4 text-sm text-slate-600">
            <span>Tutor: {{ booking?.tutor_name }}</span>
            <span>{{ booking?.subject }}</span>
          </div>
          <div class="flex justify-between py-4 text-sm text-slate-600">
            <span
              >Date:
              {{
                booking?.start_time ? fmtDate(booking.start_time) : "N/A"
              }}</span
            >
            <span
              >Time:
              {{
                booking?.start_time ? fmtTime(booking.start_time) : "N/A"
              }}</span
            >
          </div>
          <div class="flex justify-between py-4 text-sm text-slate-600">
            <span>Booking #{{ booking?.sessionId ? booking.sessionId : "N/A" }}</span>
          </div>
        </div>
        <div class="rounded-xl bg-slate-50 p-4 text-center">
          <p class="text-sm font-semibold text-slate-700">
            Payment cancelled • No charge applied
          </p>
        </div>
      </div>

      <!-- Try Again Section -->
      <div class="space-y-6">
        <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <h3 class="text-xl font-bold text-slate-900 mb-4">Try again?</h3>
          <div class="space-y-4">
            <div
              class="flex items-center gap-3 rounded-lg bg-slate-50 border-l-4 border-yellow-500 p-4"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-100 text-yellow-700 font-bold"
              >
                !
              </div>
              <div>
                <p class="font-semibold text-slate-900">No payment was taken</p>
                <p class="text-sm text-slate-600">
                  Your card was not charged. Try again anytime.
                </p>
              </div>
            </div>
            <div
              class="flex items-center gap-3 rounded-lg bg-emerald-50 border-l-4 border-emerald-500 p-4"
            >
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-bold"
              >
                ✓
              </div>
              <div>
                <p class="font-semibold text-slate-900">
                  Booking still available
                </p>
                <p class="text-sm text-slate-600">
                  {{ booking?.tutor_name }} is still available for your
                  preferred time.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <button
            @click="startCheckout"
            class="rounded-xl bg-blue-600 px-6 py-4 text-center font-semibold text-white transition hover:bg-blue-700"
          >
            Retry Payment
          </button>
          <RouterLink
            to="/tutors"
            class="rounded-xl border border-slate-300 bg-white px-6 py-4 text-center font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Change Tutor
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div
      class="mt-16 rounded-2xl bg-slate-900 p-8 text-white text-center border border-slate-800"
    >
      <h3 class="text-2xl font-bold">Need help?</h3>
      <p class="mt-2 text-slate-300">
        Contact support if you encountered any issues with payment.
      </p>
      <RouterLink
        to="/support"
        class="mt-6 inline-block rounded-xl bg-yellow-500 px-8 py-4 font-semibold text-white transition hover:bg-yellow-600"
      >
        Contact Support
      </RouterLink>
    </div>
  </section>
</template>
