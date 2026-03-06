<script setup lang="ts">
const heroTutors = [
  { name: 'James Tan', subject: 'A-Level Mathematics', rating: '4.9', rate: '65', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=James' },
  { name: 'Sarah Lim', subject: 'A-Level Chemistry', rating: '4.8', rate: '70', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=Sarah' },
  { name: 'Priya Sharma', subject: 'A-Level General Paper', rating: '4.9', rate: '55', avatar: 'https://api.dicebear.com/9.x/notionists/svg?seed=Priya' },
]
const stats = [
  { value: '200+', label: 'Verified Tutors' },
  { value: '5,000+', label: 'Students' },
  { value: '15,000+', label: 'Sessions Booked' },
  { value: '4.8', label: 'Average Rating' },
]
const steps = [
  { title: 'Search & Discover', desc: 'Browse qualified tutors by subject, level, and availability. Read reviews from real students.', color: '#4A90D9' },
  { title: 'Book a Session', desc: 'Choose an available time slot, confirm your booking, and pay securely via Stripe.', color: '#2EAA4F' },
  { title: 'Learn & Excel', desc: 'Join your live session via Google Meet. After the lesson, rate your tutor.', color: '#1B3A5C' },
]
const features = [
  { title: 'Smart Tutor Matching', desc: 'Find tutors based on subject, level, price range, and student reviews.', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { title: 'Live Google Meet', desc: 'Every session comes with an auto-generated Google Meet link.', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
  { title: 'Secure Payments', desc: 'Pay safely via Stripe. All transactions are encrypted.', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { title: 'Reviews & Ratings', desc: 'Read authentic reviews from other students.', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
  { title: 'Calendar Sync', desc: 'Sessions automatically added to your Google Calendar.', bg: '#E8F0FE', iconColor: '#4A90D9' },
  { title: 'Email Notifications', desc: 'Receive instant email confirmations for bookings and reminders.', bg: 'rgba(46,170,79,0.1)', iconColor: '#2EAA4F' },
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
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-6" style="background-color:rgba(255,255,255,0.15);color:#fff">
              <span class="w-2 h-2 rounded-full" style="background-color:#2EAA4F"></span>Trusted by 5,000+ students in Singapore
            </div>
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-tight" style="text-wrap:balance">Find Your <span style="color:#2EAA4F">Perfect Tutor</span> in Singapore</h1>
            <p class="mt-6 text-lg md:text-xl leading-relaxed" style="color:rgba(255,255,255,0.85);text-wrap:balance">Connect with highly qualified, MOE-registered tutors for O-Level, A-Level, and IB subjects. Book sessions, learn via Google Meet, and excel in your exams.</p>
            <div class="mt-8 flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
              <router-link to="/signup" class="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold text-white transition-all duration-200 hover:scale-105 shadow-lg" style="background-color:#2EAA4F">Start Learning Today</router-link>
              <router-link to="/tutors" class="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold transition-all duration-200 hover:scale-105" style="background-color:rgba(255,255,255,0.15);color:#fff;backdrop-filter:blur(8px)">Browse Tutors</router-link>
            </div>
            <div class="mt-10 flex flex-wrap items-center gap-6 justify-center lg:justify-start">
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5" style="color:#2EAA4F" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-sm font-medium text-white">Verified Tutors</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5" style="color:#2EAA4F" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-sm font-medium text-white">Google Meet Sessions</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5" style="color:#2EAA4F" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="text-sm font-medium text-white">Secure Payments</span>
              </div>
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

    <section class="py-16 border-b" style="background-color:#fff;border-color:#E8F0FE">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="stat in stats" :key="stat.label" class="text-center">
            <p class="text-3xl md:text-4xl font-extrabold" style="color:#4A90D9">{{ stat.value }}</p>
            <p class="mt-1 text-sm font-medium" style="color:#1B3A5C;opacity:0.7">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20" style="background-color:#F5F7FA">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <p class="text-sm font-semibold uppercase tracking-wider mb-3" style="color:#4A90D9">How It Works</p>
          <h2 class="text-3xl md:text-4xl font-extrabold" style="color:#1B3A5C;text-wrap:balance">Start learning in 3 simple steps</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="(step,i) in steps" :key="i" class="relative">
            <div class="rounded-2xl p-8 transition-all duration-300 hover:-translate-y-1 border" style="background-color:#fff;border-color:#E8F0FE">
              <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-6 text-white font-bold text-lg" :style="{backgroundColor:step.color}">{{ i+1 }}</div>
              <h3 class="text-xl font-bold mb-3" style="color:#1B3A5C">{{ step.title }}</h3>
              <p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.7">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20" style="background-color:#fff">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <p class="text-sm font-semibold uppercase tracking-wider mb-3" style="color:#2EAA4F">Features</p>
          <h2 class="text-3xl md:text-4xl font-extrabold" style="color:#1B3A5C;text-wrap:balance">Everything you need to excel</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="(f,i) in features" :key="i" class="p-6 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg" style="border-color:#E8F0FE;background-color:#fff">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center mb-5" :style="{backgroundColor:f.bg}">
              <svg class="w-6 h-6" :style="{color:f.iconColor}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="text-lg font-bold mb-2" style="color:#1B3A5C">{{ f.title }}</h3>
            <p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.7">{{ f.desc }}</p>
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
        <router-link to="/signup" class="inline-block px-10 py-4 rounded-xl text-lg font-bold transition-all duration-200 hover:scale-105 shadow-lg" style="background-color:#2EAA4F;color:#fff">Get Started for Free</router-link>
      </div>
    </section>
  </div>
</template>
