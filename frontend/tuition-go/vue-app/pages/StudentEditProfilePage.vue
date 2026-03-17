<script setup lang="ts">
import { ref, watch } from 'vue'
import { useUser } from '@clerk/vue'
import { useStudentService } from '../services/studentService'
import { useRouter } from 'vue-router'

const { user, isLoaded } = useUser()
const studentService = useStudentService()
const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const success = ref(false)
const error = ref<string | null>(null)
const studentId = ref<string | null>(null)

const form = ref({
  name: '',
  email: '',
  phone: '',
  profileImage: null as File | null,
})

const avatarPreview = ref('')

async function loadProfile() {
  loading.value = true
  error.value = null
  try {
    const metadata = user.value?.unsafeMetadata as Record<string, unknown> | undefined
    studentId.value = typeof metadata?.studentId === 'string' ? metadata.studentId : null

    if (!studentId.value) {
      error.value = 'Student profile not linked to this account.'
      return
    }

    const { data } = await studentService.getById(studentId.value)
    form.value.name = data.name || ''
    form.value.email = data.email || ''
    form.value.phone = data.phone || ''
    avatarPreview.value = data.imageURL || ''
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load profile.'
    console.error('Error loading profile:', err)
  } finally {
    loading.value = false
  }
}

function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  form.value.profileImage = file
  const reader = new FileReader()
  reader.onload = (ev) => { avatarPreview.value = ev.target?.result as string }
  reader.readAsDataURL(file)
}

async function handleSubmit() {
  if (!studentId.value) return

  saving.value = true
  error.value = null
  success.value = false

  try {
    const formData = new FormData()
    formData.append('name', form.value.name)
    formData.append('phone', form.value.phone)
    if (form.value.profileImage) {
      formData.append('profileImage', form.value.profileImage)
    }

    const { data } = await studentService.update(studentId.value, formData)
    // Update the avatar preview with the new URL from the server
    if (data?.data?.imageURL) {
      avatarPreview.value = data.data.imageURL
    }
    form.value.profileImage = null
    success.value = true
    setTimeout(() => { success.value = false }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to update profile.'
    console.error('Error updating profile:', err)
  } finally {
    saving.value = false
  }
}

watch(
  () => isLoaded.value,
  (loaded) => {
    if (loaded) loadProfile()
  },
  { immediate: true }
)
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <button @click="router.back()" class="flex items-center gap-1.5 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Back
      </button>

      <div class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">
        <!-- Header with avatar upload -->
        <div class="p-6 md:p-8" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
          <div class="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            <div class="relative group">
              <img
                :src="avatarPreview || 'https://api.dicebear.com/9.x/notionists/svg?seed=Student'"
                alt="Profile photo"
                class="w-20 h-20 rounded-2xl object-cover shadow-lg"
                crossorigin="anonymous"
                style="background-color:#E8F0FE"
              />
              <label class="absolute inset-0 rounded-2xl flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer" style="background-color:rgba(27,58,92,0.6);transition:opacity 0.2s">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <circle cx="12" cy="13" r="3"/>
                </svg>
                <input type="file" accept="image/*" class="hidden" @change="handleFileUpload"/>
              </label>
            </div>
            <div>
              <h1 class="text-2xl font-extrabold text-white">My Profile</h1>
              <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">{{ form.name }} · {{ form.email }}</p>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin">
            <svg class="w-8 h-8" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </div>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="p-6 md:p-8 space-y-6">
          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Name</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <input
                v-model="form.name"
                type="text"
                required
                placeholder="Your full name"
                class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2"
                style="border-color:#E8F0FE;color:#1B3A5C"
              />
            </div>
          </div>

          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Email</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2" style="color:#4A90D9;opacity:0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <input
                :value="form.email"
                type="email"
                disabled
                class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border cursor-not-allowed"
                style="border-color:#E8F0FE;color:rgba(27,58,92,0.5);background-color:#F5F7FA"
              />
            </div>
            <p class="text-xs mt-1" style="color:rgba(27,58,92,0.4)">Email cannot be changed</p>
          </div>

          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Phone Number</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              <input
                v-model="form.phone"
                type="tel"
                placeholder="+65 9123 4567"
                class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2"
                style="border-color:#E8F0FE;color:#1B3A5C"
              />
            </div>
          </div>

          <div v-if="error" class="px-4 py-3 rounded-xl text-sm font-medium" style="background-color:rgba(239,68,68,0.1);color:#ef4444">
            {{ error }}
          </div>

          <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2" style="border-top:1px solid #E8F0FE">
            <div v-if="form.profileImage" class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full" style="background-color:#F5A623"></span>
              <p class="text-xs font-medium" style="color:#1B3A5C;opacity:0.6">New photo selected</p>
            </div>
            <div v-else></div>
            <div class="flex items-center gap-3">
              <button type="button" @click="router.back()" class="px-6 py-3 rounded-xl text-sm font-semibold" style="color:#1B3A5C;background-color:#F5F7FA;border:1px solid #E8F0FE">Cancel</button>
              <button
                type="submit"
                :disabled="saving"
                class="px-8 py-3 rounded-xl text-sm font-bold text-white shadow-md hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
                style="background-color:#4A90D9"
              >
                <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- Success toast -->
      <div v-if="success" class="fixed bottom-6 right-6 flex items-center gap-3 px-5 py-4 rounded-xl shadow-lg" style="background-color:#fff;border:1px solid #E8F0FE;z-index:50">
        <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background-color:rgba(46,170,79,0.1)">
          <svg class="w-4 h-4" style="color:#2EAA4F" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <div>
          <p class="text-sm font-bold" style="color:#1B3A5C">Profile Updated</p>
          <p class="text-xs" style="color:rgba(27,58,92,0.6)">Your changes have been saved successfully.</p>
        </div>
      </div>
    </div>
  </div>
</template>
