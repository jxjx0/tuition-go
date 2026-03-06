<script setup lang="ts">
// No logic needed for now
</script>

<template>
  <footer style="background-color:#1B3A5C;color:#fff">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
        <div class="md:col-span-1">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background:linear-gradient(135deg,#4A90D9,#2EAA4F)">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </div>
            <span class="text-xl font-bold text-white">EduMatch</span>
          </div>
          <p class="text-sm leading-relaxed" style="color:rgba(255,255,255,0.7)">Singapore's trusted platform connecting students with qualified tutors.</p>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color:#4A90D9">Platform</h4>
          <ul class="space-y-3">
            <li><router-link to="/tutors" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Browse Tutors</router-link></li>
            <li><router-link to="/dashboard" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Student Dashboard</router-link></li>
            <li><router-link to="/tutor-dashboard" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Tutor Portal</router-link></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color:#4A90D9">Popular Subjects</h4>
          <ul class="space-y-3">
            <li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Mathematics</span></li>
            <li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Chemistry</span></li>
            <li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Physics</span></li>
            <li><span class="text-sm" style="color:rgba(255,255,255,0.7)">English & GP</span></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color:#4A90D9">Support</h4>
          <ul class="space-y-3">
            <li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Help Centre</a></li>
            <li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Privacy Policy</a></li>
            <li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Terms of Service</a></li>
          </ul>
        </div>
      </div>
      <div class="mt-12 pt-8 border-t flex flex-col sm:flex-row items-center justify-between gap-4" style="border-color:rgba(255,255,255,0.15)">
        <p class="text-sm" style="color:rgba(255,255,255,0.5)">2026 EduMatch. All rights reserved. Built by G4T4.</p>
        <div class="flex items-center gap-4">
          <span class="text-xs px-3 py-1 rounded-full" style="background-color:rgba(74,144,217,0.2);color:#4A90D9">IS213 Project</span>
          <span class="text-xs px-3 py-1 rounded-full" style="background-color:rgba(46,170,79,0.2);color:#2EAA4F">ESD G4T4</span>
        </div>
      </div>
    </div>
  </footer>
</template>
