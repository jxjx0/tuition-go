<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth, useUser, useClerk } from '@clerk/vue'


const route = useRoute()
const router = useRouter()
const showMobile = ref(false)
const showUserMenu = ref(false)

const { isSignedIn } = useAuth()
const { user } = useUser()
const clerk = useClerk()

const isLoggedIn = computed(() => isSignedIn.value ?? false)
const userRole = computed(() => {
  const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
  return typeof metadata?.role === 'string' ? metadata.role : null
})

const tutorProfileLink = computed(() => {
  if (!user.value) return null

  const metadata = user.value.unsafeMetadata as Record<string, unknown> | undefined
  const tutorId = metadata?.tutorId

  if (userRole.value === 'tutor' && typeof tutorId === 'string') {
    return {
      to: `/tutor-profile/${tutorId}`,
      label: 'My Profile'
    }
  }

  return null
})

watch(() => user.value, (u) => {
  console.log("Clerk metadata:", u?.unsafeMetadata)
}, { immediate: true })

// Auto-assign 'student' role if user signed in without one
// and redirect to correct dashboard based on role
watch(() => user.value, async (u) => {
  if (u && !u.unsafeMetadata?.role) {
    await u.update({
      unsafeMetadata: { ...u.unsafeMetadata, role: 'student' },
    })
  }
  if (u && u.unsafeMetadata?.role && route.path === '/dashboard' && u.unsafeMetadata.role === 'tutor') {
    router.replace('/tutor-dashboard')
  }
}, { immediate: true })
const userName = computed(() => user.value?.fullName ?? user.value?.firstName ?? 'User')
const userAvatar = computed(() => user.value?.imageUrl ?? 'https://api.dicebear.com/9.x/notionists/svg?seed=User')

const dashboardLink = computed(() => {
  if (!isLoggedIn.value) return null
  if (userRole.value === 'tutor') return { to: '/tutor-dashboard', label: 'Tutor Portal' }
  return { to: '/dashboard', label: 'My Sessions' }
})

const navLinks = computed(() => {
  const links: { to: string; label: string }[] = []
  if (isLoggedIn.value) links.push({ to: '/tutors', label: 'Browse Tutors' })
  if (dashboardLink.value) links.push(dashboardLink.value)
  return links
})

function isActive(path: string) {
  return route.path === path
}

async function handleLogout() {
  showUserMenu.value = false
  await clerk.value?.signOut()
  router.push('/')
}
</script>

<template>
  <nav class="sticky top-0 z-50 border-b" style="background-color:#fff;border-color:#E8F0FE">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <router-link to="/" class="flex items-center gap-2.5">
          <!-- Logo: replace /logo.png with your actual logo file placed in the public folder -->
          <img src="/logo.png" alt="TuitionGo" class="h-20 w-auto object-contain"
               @error="(e) => (e.target as HTMLImageElement).style.display='none'"/>
          <span class="text-xl font-bold tracking-tight" style="color:#1B3A5C">TuitionGo</span>
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
                <svg class="w-4 h-4" :class="{'rotate-180':showUserMenu}" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-if="showUserMenu" class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border py-2 z-50" style="border-color:#E8F0FE">
                <router-link
                  v-if="userRole !== 'tutor'"
                  to="/student-profile"
                  @click="showUserMenu=false"
                  class="block px-4 py-2.5 text-sm hover:bg-gray-50"
                  style="color:#1B3A5C"
                >
                  My Profile
                </router-link>
                <router-link
                  v-if="tutorProfileLink"
                  :to="tutorProfileLink.to"
                  @click="showUserMenu = false"
                  class="block px-4 py-2.5 text-sm hover:bg-gray-50"
                  style="color:#1B3A5C">
                  {{ tutorProfileLink.label }}
                </router-link>
                <div class="border-t my-1" style="border-color:#E8F0FE"></div>
                <button @click="handleLogout" class="block px-4 py-2.5 text-sm hover:bg-red-50 w-full text-left" style="color:#ef4444">Logout</button>
              </div>
            </div>
          </template>
        </div>
        <button @click="showMobile=!showMobile" class="md:hidden p-2 rounded-lg hover:bg-gray-100">
          <svg v-if="!showMobile" class="w-6 h-6" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <svg v-else class="w-6 h-6" style="color:#1B3A5C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>
    <div v-if="showMobile" class="md:hidden border-t bg-white" style="border-color:#E8F0FE">
      <div class="px-4 py-3 space-y-1">
        <router-link v-for="link in navLinks" :key="link.to" :to="link.to" @click="showMobile=false" class="block px-4 py-2.5 rounded-lg text-sm font-medium" :style="isActive(link.to)?'background-color:#E8F0FE;color:#4A90D9':'color:#1B3A5C'">{{ link.label }}</router-link>
        <template v-if="!isLoggedIn">
          <div class="pt-3 border-t flex flex-col gap-2" style="border-color:#E8F0FE">
            <router-link to="/login" @click="showMobile=false" class="px-4 py-2.5 text-sm font-medium rounded-lg text-center w-full block" style="color:#4A90D9">Log In</router-link>
            <router-link to="/signup" @click="showMobile=false" class="px-4 py-2.5 text-sm font-semibold rounded-lg text-white text-center w-full block" style="background-color:#4A90D9">Sign Up Free</router-link>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>
