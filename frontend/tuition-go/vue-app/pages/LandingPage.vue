<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { SignInButton, SignUpButton } from '@clerk/vue'

const heroTutors = [
  { name: 'James Tan', subject: 'A-Level Mathematics', rating: '4.9', rate: '65', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=James' },
  { name: 'Sarah Lim', subject: 'A-Level Chemistry', rating: '4.8', rate: '70', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=Sarah' },
  { name: 'Priya Sharma', subject: 'A-Level General Paper', rating: '4.9', rate: '55', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=Priya' },
]
const steps = [
  {
    label: 'STEP 01',
    title: 'Search & Discover',
    desc: 'Browse qualified tutors by subject, level, and availability. Read authentic reviews from real students to find your perfect match.',
    color: '#4A90D9',
    iconBg: '#E8F0FE',
    icon: 'search',
  },
  {
    label: 'STEP 02',
    title: 'Book a Session',
    desc: 'Choose an available time slot that fits your schedule, confirm your booking, and pay securely via Stripe.',
    color: '#2EAA4F',
    iconBg: 'rgba(46,170,79,0.12)',
    icon: 'calendar',
  },
  {
    label: 'STEP 03',
    title: 'Learn & Excel',
    desc: 'Join your live session via an auto-generated Google Meet link. After the lesson, rate your tutor to help others.',
    color: '#1B3A5C',
    iconBg: '#E8F0FE',
    icon: 'star',
  },
]

const stepRefs = ref<HTMLElement[]>([])

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('step-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.15 }
  )
  stepRefs.value.forEach((el) => el && observer.observe(el))
})
const whyFeatures = [
  {
    title: 'Google Meet & Calendar Sync',
    desc: 'When tutors create a session, a Google Meet link is auto-generated and synced directly to their Google Calendar — no manual setup needed.',
    icon: 'meet',
  },
  {
    title: 'Secure Payments via Stripe',
    desc: 'Students pay securely through Stripe at the time of booking. All transactions are encrypted and processed safely.',
    icon: 'stripe',
  },
  {
    title: 'Email Alerts for Cancellations',
    desc: 'Tutors and students are automatically notified by email whenever a session is cancelled, keeping everyone informed instantly.',
    icon: 'email',
  },
]
const testimonials = [
  { name: 'Rachel Tan', role: 'A-Level Student, ACJC', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=Rachel', quote: 'EduMatch helped me find the perfect Math tutor. My grades went from C to A in just 4 months!' },
  { name: 'Mrs. Koh', role: 'Parent of O-Level Student', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=MrsKoh', quote: 'As a working parent, I love that I can easily book and manage my son\'s tuition sessions.' },
  { name: 'David Lim', role: 'IB Student, UWC SEA', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=David', quote: 'The tutors here are incredibly qualified. Sarah helped me score a 7 for IB Chemistry.' },
]
</script>

<template>
  <div>
    <section class="relative overflow-hidden" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 left-10 w-72 h-72 rounded-full" style="background-color:#4A90D9;filter:blur(100px)"></div>
        <div class="absolute bottom-10 right-20 w-96 h-96 rounded-full" style="background-color:#2EAA4F;filter:blur(120px)"></div>
      </div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 relative z-10">
        <div class="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
          <div class="flex-1 text-center lg:text-left">
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-tight" style="text-wrap:balance">Find Your <span style="color:#2EAA4F">Perfect Tutor</span> in Singapore</h1>
            <p class="mt-6 text-lg md:text-xl leading-relaxed" style="color:rgba(255,255,255,0.85);text-wrap:balance">Connect with highly qualified, MOE-registered tutors for O-Level, A-Level, and IB subjects. Book sessions, learn via Google Meet, and excel in your exams.</p>
            <div class="mt-8 flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
              <SignInButton mode="modal" fallback-redirect-url="/#/dashboard">
                <button class="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold text-white transition-all duration-200 hover:scale-105 shadow-lg" style="background-color:#2EAA4F">Start Learning Today</button>
              </SignInButton>
              <router-link to="/tutors" class="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold transition-all duration-200 hover:scale-105" style="background-color:rgba(255,255,255,0.15);color:#fff;backdrop-filter:blur(8px)">Browse Tutors</router-link>
            </div>
          </div>
          <div class="flex-1 w-full max-w-md lg:max-w-lg">
            <div class="rounded-2xl p-6 shadow-2xl" style="background-color:rgba(255,255,255,0.1);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.2)">
              <div class="space-y-4">
                <div v-for="(t,i) in heroTutors" :key="i" class="flex items-center gap-4 p-4 rounded-xl bg-white shadow-sm" :style="{opacity:1-i*0.1}">
                  <img :src="t.avatar" :alt="t.name" class="w-12 h-12 rounded-full" crossorigin="anonymous"/>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <p class="font-semibold text-sm truncate" style="color:#1B3A5C">{{ t.name }}</p>
                      <svg class="w-4 h-4 flex-shrink-0" style="color:#4A90D9" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>
                    </div>
                    <p class="text-xs truncate" style="color:#4A90D9">{{ t.subject }}</p>
                  </div>
                  <div class="text-right flex-shrink-0">
                    <div class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="#F59E0B" viewBox="0 0 24 24">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                      </svg>
                      <span class="text-sm font-bold" style="color:#1B3A5C">{{ t.rating }}</span>
                    </div>
                    <p class="text-xs font-semibold" style="color:#2EAA4F">${{ t.rate }}/hr</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>


    <section class="py-20" style="background-color:#F5F7FA">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-extrabold" style="color:#1B3A5C;text-wrap:balance">How It Works</h2>
          <p class="mt-3 text-base" style="color:#1B3A5C;opacity:0.6">Three simple steps to start learning with your perfect tutor</p>
        </div>
        <div class="space-y-20">
          <div
            v-for="(step, i) in steps"
            :key="i"
            :ref="el => { if (el) stepRefs[i] = el as HTMLElement }"
            class="step-fade flex flex-col md:flex-row items-center gap-10"
            :class="i % 2 === 1 ? 'md:flex-row-reverse' : ''"
          >
            <!-- Icon card -->
            <div class="flex-shrink-0">
              <div class="w-48 h-48 rounded-3xl flex items-center justify-center shadow-md border" :style="{ backgroundColor: '#fff', borderColor: '#E8F0FE' }">
                <div class="w-24 h-24 rounded-2xl flex items-center justify-center" :style="{ backgroundColor: step.iconBg }">
                  <!-- Search icon -->
                  <svg v-if="step.icon === 'search'" class="w-12 h-12" :style="{ color: step.color }" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
                  </svg>
                  <!-- Calendar icon -->
                  <svg v-else-if="step.icon === 'calendar'" class="w-12 h-12" :style="{ color: step.color }" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2z"/>
                  </svg>
                  <!-- Star icon -->
                  <svg v-else-if="step.icon === 'star'" class="w-12 h-12" :style="{ color: step.color }" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 0 0 .95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 0 0-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 0 0-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 0 0-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 0 0 .951-.69l1.519-4.674z"/>
                  </svg>
                </div>
              </div>
            </div>
            <!-- Text -->
            <div class="flex-1 text-center md:text-left" :class="i % 2 === 1 ? 'md:text-right' : ''">
              <p class="text-xs font-bold uppercase tracking-widest mb-2" :style="{ color: step.color }">{{ step.label }}</p>
              <h3 class="text-2xl font-extrabold mb-3" style="color:#1B3A5C">{{ step.title }}</h3>
              <p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.7">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col lg:flex-row items-center gap-14">
          <!-- Left illustration card -->
          <div class="flex-shrink-0">
            <div class="w-56 h-56 rounded-3xl flex items-center justify-center shadow-xl" style="background-color:#fff">
              <div class="w-28 h-28 flex items-center justify-center">
                <!-- Graduation cap with sparkle — represents tuition -->
                <svg viewBox="0 0 64 64" fill="none" class="w-full h-full">
                  <path d="M32 10L6 24l26 14 26-14L32 10z" fill="#1B3A5C"/>
                  <path d="M18 31v12c0 4 6.268 8 14 8s14-4 14-8V31" stroke="#1B3A5C" stroke-width="2.5" stroke-linecap="round"/>
                  <circle cx="52" cy="24" r="3" fill="#4A90D9"/>
                  <line x1="52" y1="24" x2="52" y2="38" stroke="#4A90D9" stroke-width="2.5" stroke-linecap="round"/>
                  <circle cx="52" cy="40" r="2.5" fill="#2EAA4F"/>
                  <path d="M10 16l-2-3M8 16l3-1" stroke="#2EAA4F" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </div>
            </div>
          </div>
          <!-- Right content -->
          <div class="flex-1">
            <h2 class="text-3xl md:text-4xl font-extrabold text-white mb-3" style="text-wrap:balance">Why use Tuition Go?</h2>
            <p class="text-base mb-10" style="color:rgba(255,255,255,0.65)">Built for tutors and students — everything just works.</p>
            <div class="space-y-4">
              <div v-for="(f, i) in whyFeatures" :key="i" class="flex items-start gap-5 p-5 rounded-2xl" style="background-color:rgba(255,255,255,0.08)">
                <div class="flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center" style="background-color:#fff">
                  <!-- Google Calendar brand icon -->
                  <svg v-if="f.icon === 'meet'" viewBox="0 0 24 24" class="w-6 h-6">
                    <path d="M19.5 3h-3V1.5H15V3H9V1.5H7.5V3h-3C3.675 3 3 3.675 3 4.5v15c0 .825.675 1.5 1.5 1.5h15c.825 0 1.5-.675 1.5-1.5v-15c0-.825-.675-1.5-1.5-1.5zm0 16.5h-15V9h15v10.5zM7.5 6H6V4.5h1.5V6zm9 0H15V4.5h1.5V6z" fill="#4285F4"/>
                    <rect x="7" y="11" width="3" height="3" rx="0.5" fill="#34A853"/>
                    <rect x="10.5" y="11" width="3" height="3" rx="0.5" fill="#FBBC05"/>
                    <rect x="14" y="11" width="3" height="3" rx="0.5" fill="#EA4335"/>
                    <rect x="7" y="14.5" width="3" height="3" rx="0.5" fill="#EA4335"/>
                    <rect x="10.5" y="14.5" width="3" height="3" rx="0.5" fill="#4285F4"/>
                  </svg>
                  <!-- Stripe brand icon (Simple Icons path, MIT licensed) -->
                  <svg v-else-if="f.icon === 'stripe'" viewBox="0 0 24 24" class="w-6 h-6" fill="#635BFF">
                    <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.594-7.305h.003z"/>
                  </svg>
                  <!-- Email icon -->
                  <svg v-else-if="f.icon === 'email'" class="w-5 h-5" fill="none" stroke="#4A90D9" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                </div>
                <div>
                  <p class="font-bold text-white mb-1">{{ f.title }}</p>
                  <p class="text-sm leading-relaxed" style="color:rgba(255,255,255,0.65)">{{ f.desc }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20" style="background-color:#E8F0FE">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <p class="text-sm font-semibold uppercase tracking-wider mb-3" style="color:#4A90D9">Testimonials</p>
          <h2 class="text-3xl md:text-4xl font-extrabold" style="color:#1B3A5C;text-wrap:balance">Loved by students and parents</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="(t,i) in testimonials" :key="i" class="p-6 rounded-2xl bg-white shadow-sm border transition-all duration-300 hover:-translate-y-1" style="border-color:rgba(74,144,217,0.1)">
            <div class="flex items-center gap-1 mb-4">
              <svg v-for="s in 5" :key="s" class="w-4 h-4" fill="#F59E0B" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <p class="text-sm leading-relaxed mb-6" style="color:#1B3A5C;opacity:0.85">"{{ t.quote }}"</p>
            <div class="flex items-center gap-3">
              <img :src="t.avatar" :alt="t.name" class="w-10 h-10 rounded-full" crossorigin="anonymous"/>
              <div>
                <p class="text-sm font-semibold" style="color:#1B3A5C">{{ t.name }}</p>
                <p class="text-xs" style="color:#4A90D9">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
      <div class="max-w-3xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-extrabold text-white mb-6" style="text-wrap:balance">Ready to ace your exams?</h2>
        <p class="text-lg mb-8" style="color:rgba(255,255,255,0.85)">Join thousands of Singapore students already learning with EduMatch. Sign up now and get your first session at 20% off.</p>
        <SignInButton mode="modal" fallback-redirect-url="/#/dashboard">
          <button class="inline-block px-10 py-4 rounded-xl text-lg font-bold transition-all duration-200 hover:scale-105 shadow-lg" style="background-color:#2EAA4F;color:#fff">Get Started for Free</button>
        </SignInButton>
      </div>
    </section>
  </div>
</template>

<style scoped>
.step-fade {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.step-fade:nth-child(2) { transition-delay: 0.1s; }
.step-fade:nth-child(3) { transition-delay: 0.2s; }
.step-visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
