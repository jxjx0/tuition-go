<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";
import { onMounted } from "vue";

const route = useRoute();
const sessionId = route.query.session_id as string;

onMounted(async () => {
  // Optional: Verify payment status with Stripe
  if (sessionId) {
    try {
      // Call your backend to verify the session
      await fetch("/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (error) {
      console.error("Payment verification failed:", error);
    }
  }
});
</script>

<template>
  <section class="mx-auto max-w-4xl px-6 py-24">
    <!-- Success Banner -->
    <div
      class="mx-auto flex w-fit items-center gap-4 rounded-2xl bg-emerald-50 p-6 shadow-xl"
    >
      <div
        class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500 text-xl font-bold text-white"
      >
        ✓
      </div>
      <div>
        <h1 class="text-2xl font-bold text-emerald-900">Payment Successful!</h1>
        <p class="text-emerald-800">Your booking has been confirmed.</p>
      </div>
    </div>

    <div class="mt-12 grid gap-12 md:grid-cols-2">
      <!-- Payment Summary -->
      <div class="space-y-6 rounded-2xl bg-white p-8 shadow-lg">
        <h2 class="text-2xl font-bold text-slate-900">Payment Summary</h2>
        <div class="divide-y divide-slate-200">
          <div class="flex justify-between py-4">
            <span class="text-lg font-semibold text-slate-900"
              >Trial Lesson</span
            >
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
            Paid via Stripe • Transaction ID:
            <span class="font-mono">sess_xxx</span>
          </p>
        </div>
      </div>

      <!-- Next Steps - Updated -->
      <div
        class="space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"
      >
        <h3 class="text-xl font-bold text-slate-900">What's next?</h3>
        <ol class="space-y-4">
          <li
            class="flex items-start gap-3 rounded-lg border-l-4 border-emerald-500 bg-slate-50 p-4 pl-4"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-bold"
              >1</span
            >
            <div>
              <p class="font-semibold text-slate-900">Check your email</p>
              <p class="text-sm text-slate-600 mt-1">
                Lesson details and Zoom link sent to student@example.com
              </p>
            </div>
          </li>
          <li
            class="flex items-start gap-3 rounded-lg border-l-4 border-blue-500 bg-slate-50 p-4 pl-4"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-bold"
              >2</span
            >
            <div>
              <p class="font-semibold text-slate-900">Join your lesson</p>
              <p class="text-sm text-slate-600 mt-1">
                Click the Zoom link at lesson time
              </p>
            </div>
          </li>
          <li
            class="flex items-start gap-3 rounded-lg border-l-4 border-indigo-500 bg-slate-50 p-4 pl-4"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold"
              >3</span
            >
            <div>
              <p class="font-semibold text-slate-900">Rate your lesson</p>
              <p class="text-sm text-slate-600 mt-1">
                Share feedback after class to help other students
              </p>
            </div>
          </li>
        </ol>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div class="mt-16 rounded-2xl bg-slate-900 p-8 text-white text-center">
      <h3 class="text-2xl font-bold">Ready for your next lesson?</h3>
      <p class="mt-2 text-slate-300">
        Your tutor was great? Book more lessons with the same flow.
      </p>
      <RouterLink
        to="/tutors"
        class="mt-6 inline-block rounded-xl bg-emerald-500 px-8 py-4 font-semibold text-white transition hover:bg-emerald-600"
      >
        Find More Tutors
      </RouterLink>
    </div>
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
