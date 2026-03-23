<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { onMounted } from 'vue'

const route = useRoute()

const startCheckout = () => {
  // Your existing startCheckout logic
  window.location.href = '/payment' // or emit to parent
}

onMounted(() => {
  // Optional: Log the failed attempt for analytics
  console.log('Payment cancelled/failed')
})
</script>

<template>
  <section class="mx-auto max-w-4xl px-6 py-24">
    <!-- Failed Banner -->
    <div class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-yellow-50 p-6 shadow-xl border border-yellow-200">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-500 text-xl font-bold text-white">
        !
      </div>
      <div>
        <h1 class="text-2xl font-bold text-yellow-900">Payment Not Completed</h1>
        <p class="text-yellow-800">Your booking is not confirmed yet.</p>
      </div>
    </div>

    <div class="mt-12 grid gap-12 md:grid-cols-2">
      <!-- Payment Summary -->
      <div class="space-y-6 rounded-2xl bg-white border border-slate-200 p-8 shadow-lg">
        <h2 class="text-2xl font-bold text-slate-900">Payment Summary</h2>
        <div class="divide-y divide-slate-200">
          <div class="flex justify-between py-4">
            <span class="text-lg font-semibold text-slate-900">Trial Lesson</span>
            <span class="text-2xl font-bold text-slate-900 line-through text-yellow-500">SGD 30.00</span>
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
            Payment cancelled • No charge applied
          </p>
        </div>
      </div>

      <!-- Try Again Section -->
      <div class="space-y-6">
        <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <h3 class="text-xl font-bold text-slate-900 mb-4">Try again?</h3>
          <div class="space-y-4">
            <div class="flex items-center gap-3 rounded-lg bg-slate-50 border-l-4 border-yellow-500 p-4">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-100 text-yellow-700 font-bold">!</div>
              <div>
                <p class="font-semibold text-slate-900">No payment was taken</p>
                <p class="text-sm text-slate-600">Your card was not charged. Try again anytime.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 rounded-lg bg-emerald-50 border-l-4 border-emerald-500 p-4">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-bold">✓</div>
              <div>
                <p class="font-semibold text-slate-900">Booking still available</p>
                <p class="text-sm text-slate-600">Mr. James is still available for your preferred time.</p>
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
    <div class="mt-16 rounded-2xl bg-slate-900 p-8 text-white text-center border border-slate-800">
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
