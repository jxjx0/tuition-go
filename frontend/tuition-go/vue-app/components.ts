// @ts-ignore
import { defineComponent, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

export const StarRating = defineComponent({
  name: 'StarRating',
  props: {
    modelValue: { type: Number, default: 0 },
    interactive: { type: Boolean, default: false },
    size: { type: String, default: 'md' },
    showValue: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props) {
    const hoverVal = ref(0)
    return { hoverVal }
  },
  template: `
    <div class="flex items-center" :class="size==='sm'?'gap-0.5':size==='lg'?'gap-1':'gap-0.5'">
      <template v-for="i in 5" :key="i">
        <button v-if="interactive" @click="$emit('update:modelValue',i)" @mouseenter="hoverVal=i" @mouseleave="hoverVal=0" class="transition-transform duration-150 hover:scale-110 focus:outline-none">
          <svg :class="size==='sm'?'w-4 h-4':size==='lg'?'w-7 h-7':'w-5 h-5'" viewBox="0 0 24 24" :fill="i<=(hoverVal||modelValue)?'#F59E0B':'#E5E7EB'" stroke="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </button>
        <svg v-else :class="size==='sm'?'w-4 h-4':size==='lg'?'w-7 h-7':'w-5 h-5'" viewBox="0 0 24 24" :fill="i<=Math.round(modelValue)?'#F59E0B':'#E5E7EB'" stroke="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
      </template>
      <span v-if="showValue" class="ml-1.5 font-semibold" style="color:#1B3A5C">{{ modelValue.toFixed(1) }}</span>
    </div>
  `,
})

export const Navbar = defineComponent({
  name: 'Navbar',
  components: { RouterLink },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const showMobile = ref(false)
    const showUserMenu = ref(false)
    const isLoggedIn = ref(true)
    const userName = ref('Alex Ng')
    const userAvatar = ref('https://api.dicebear.com/9.x/notionists/svg?seed=Alex')
    const navLinks = [
      { to: '/tutors', label: 'Browse Tutors' },
      { to: '/dashboard', label: 'My Sessions' },
      { to: '/tutor-dashboard', label: 'Tutor Portal' },
    ]
    function isActive(path: string) { return route.path === path }
    function handleLogout() { isLoggedIn.value = false; showUserMenu.value = false; router.push('/') }
    return { showMobile, showUserMenu, isLoggedIn, userName, userAvatar, navLinks, isActive, handleLogout }
  },
  template: `
    <nav class="sticky top-0 z-50 border-b" style="background-color:#fff;border-color:#E8F0FE">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <router-link to="/" class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background:linear-gradient(135deg,#4A90D9,#1B3A5C)"><svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg></div>
            <span class="text-xl font-bold tracking-tight" style="color:#1B3A5C">EduMatch</span>
          </router-link>
          <div class="hidden md:flex items-center gap-1">
            <router-link v-for="link in navLinks" :key="link.to" :to="link.to" class="px-4 py-2 rounded-lg text-sm font-medium transition-all" :style="isActive(link.to)?'background-color:#E8F0FE;color:#4A90D9':'color:#1B3A5C'">{{ link.label }}</router-link>
          </div>
          <div class="hidden md:flex items-center gap-3">
            <template v-if="!isLoggedIn">
              <router-link to="/login" class="px-4 py-2 text-sm font-medium rounded-lg" style="color:#4A90D9">Log In</router-link>
              <router-link to="/signup" class="px-5 py-2.5 text-sm font-semibold rounded-lg text-white shadow-sm" style="background-color:#4A90D9">Sign Up Free</router-link>
            </template>
            <template v-else>
              <div class="relative">
                <button @click="showUserMenu=!showUserMenu" class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-50">
                  <img :src="userAvatar" alt="User" class="w-8 h-8 rounded-full" crossorigin="anonymous"/>
                  <span class="text-sm font-medium" style="color:#1B3A5C">{{ userName }}</span>
                  <svg class="w-4 h-4" :class="{'rotate-180':showUserMenu}" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <div v-if="showUserMenu" class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border py-2 z-50" style="border-color:#E8F0FE">
                  <router-link to="/dashboard" @click="showUserMenu=false" class="block px-4 py-2.5 text-sm hover:bg-gray-50" style="color:#1B3A5C">Student Dashboard</router-link>
                  <router-link to="/tutor-dashboard" @click="showUserMenu=false" class="block px-4 py-2.5 text-sm hover:bg-gray-50" style="color:#1B3A5C">Tutor Dashboard</router-link>
                  <div class="border-t my-1" style="border-color:#E8F0FE"></div>
                  <button @click="handleLogout" class="block px-4 py-2.5 text-sm hover:bg-red-50 w-full text-left" style="color:#ef4444">Sign Out</button>
                </div>
              </div>
            </template>
          </div>
          <button @click="showMobile=!showMobile" class="md:hidden p-2 rounded-lg hover:bg-gray-100">
            <svg v-if="!showMobile" class="w-6 h-6" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
            <svg v-else class="w-6 h-6" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>
      <div v-if="showMobile" class="md:hidden border-t bg-white" style="border-color:#E8F0FE">
        <div class="px-4 py-3 space-y-1">
          <router-link v-for="link in navLinks" :key="link.to" :to="link.to" @click="showMobile=false" class="block px-4 py-2.5 rounded-lg text-sm font-medium" :style="isActive(link.to)?'background-color:#E8F0FE;color:#4A90D9':'color:#1B3A5C'">{{ link.label }}</router-link>
          <template v-if="!isLoggedIn">
            <div class="pt-3 border-t flex flex-col gap-2" style="border-color:#E8F0FE">
              <router-link to="/login" @click="showMobile=false" class="px-4 py-2.5 text-sm font-medium rounded-lg text-center" style="color:#4A90D9">Log In</router-link>
              <router-link to="/signup" @click="showMobile=false" class="px-4 py-2.5 text-sm font-semibold rounded-lg text-white text-center" style="background-color:#4A90D9">Sign Up Free</router-link>
            </div>
          </template>
        </div>
      </div>
    </nav>
  `,
})

export const Footer = defineComponent({
  name: 'Footer',
  components: { RouterLink },
  template: `
    <footer style="background-color:#1B3A5C;color:#fff">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
          <div class="md:col-span-1">
            <div class="flex items-center gap-2.5 mb-4">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background:linear-gradient(135deg,#4A90D9,#2EAA4F)"><svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg></div>
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
            <ul class="space-y-3"><li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Mathematics</span></li><li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Chemistry</span></li><li><span class="text-sm" style="color:rgba(255,255,255,0.7)">Physics</span></li><li><span class="text-sm" style="color:rgba(255,255,255,0.7)">English & GP</span></li></ul>
          </div>
          <div>
            <h4 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color:#4A90D9">Support</h4>
            <ul class="space-y-3"><li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Help Centre</a></li><li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Privacy Policy</a></li><li><a href="#" class="text-sm hover:text-white" style="color:rgba(255,255,255,0.7)">Terms of Service</a></li></ul>
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
  `,
})
