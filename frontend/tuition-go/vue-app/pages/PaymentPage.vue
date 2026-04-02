<script setup lang="ts">
import { useApi } from '../services/api'

const api = useApi()

async function startCheckout() {
  const { data } = await api.post(
    "/payments/create-checkout-session",

    {
      title: "Trial Lesson",
      description: "1-hour session",
      amount: 3000,
      tutor_name: "Mr. James Tan",
      subject: "Secondary Math",
      lesson_date: "2026-03-29 10:00 AM",
      booking_id: 123,
    },
  );

  window.location.href = data.url;
}
</script>

<template>
  <section
    class="mx-auto grid max-w-7xl gap-10 px-6 py-16 md:grid-cols-2 md:items-center"
  >
    <div>
      <span
        class="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
      >
        New • Fast booking flow
      </span>

      <h2 class="mt-4 text-4xl font-extrabold leading-tight md:text-5xl">
        Book the right tutor for every student
      </h2>

      <p class="mt-4 max-w-xl text-base leading-7 text-slate-600">
        Manage lessons, compare tutors, and pay securely in one simple platform
        built for students and parents.
      </p>

      <div class="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          @click="startCheckout"
          class="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Book a trial lesson
        </button>

        <button
          class="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          Browse tutors
        </button>
      </div>

      <div class="mt-8 flex gap-6 text-sm text-slate-500">
        <div>
          <p class="text-2xl font-bold text-slate-900">500+</p>
          <p>Lessons completed</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-slate-900">4.9/5</p>
          <p>Average rating</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-slate-900">24/7</p>
          <p>Booking access</p>
        </div>
      </div>
    </div>
  </section>
</template>