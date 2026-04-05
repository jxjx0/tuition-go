<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { findTutorById } from "../composables/useTutors"
import { useUser } from '@clerk/vue'

const SUBJECTS = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Chinese', 'Malay', 'Tamil', 'History', 'Geography', 'Computer Science', 'Economics', 'Accounting', 'Literature', 'Art', 'Music']
const LEVELS = ['Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6', 'Secondary 1', 'Secondary 2', 'Secondary 3', 'Secondary 4', 'JC/A-Level', 'IB', 'University']

const tabs = [
  { key: 'personal', label: 'Personal Info', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { key: 'teaching', label: 'Teaching Details', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
]

const { user, isLoaded } = useUser()

const route = useRoute()
const tutorId = computed(() => route.params.id as string)
const { tutor, searchForTutor, updateProfile, addSubject, deleteSubject, loading } = findTutorById()

const form = reactive({
  name: "",
  email: "",
  phone: "",
  password: "",
  bio: "",
  profileImage: null as File | null,
  teachingPairs: [] as any[],
  photo: null as File | null
})

const avatarPreview = ref("")
const originalData = ref("")

onMounted(() => {
  searchForTutor(tutorId.value)
});

function normalizeForm() {
  return {
    name: form.name,
    phone: form.phone,
    bio: form.bio,
    password: form.password,
    photoChanged: !!form.photo,
  };
}

watch(tutor, (t) => {
  if (!t) return;

  form.name = t.name;
  form.email = t.email;
  form.phone = t.phone?.toString() || "";
  form.bio = t.bio || "";

  avatarPreview.value = t.imageURL || '/no_image.jpg';

  form.teachingPairs = (t.subjects || []).map((s: any) => ({
    subject: s.subject,
    level: s.academicLevel,
    hourlyRate: s.hourlyRate,
    tutorSubjectId: s.tutorSubjectId,
  }));
  
  originalData.value = JSON.stringify(normalizeForm())
}, { immediate: true });

const activeTab = ref<string>('personal')
const newSubject = ref('')
const newLevel = ref('')
const newHourlyRate = ref<number | null>(null)
const pairError = ref('')
const saving = ref(false)
const saved = ref(false)
const showPassword = ref(false)
const errors = reactive<Record<string, string>>({})

const isDirty = computed(() => {
  return JSON.stringify(normalizeForm()) !== originalData.value;
});

const passwordStrength = computed(() => {
  const pw = form.password
  if (!pw) return { score: 0, label: '', color: '#E8F0FE' }
  let score = 0
  if (pw.length >= 6) score++
  if (pw.length >= 10) score++
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++
  if (/[0-9]/.test(pw) && /[^A-Za-z0-9]/.test(pw)) score++
  const map: Record<number, { label: string; color: string }> = {
    0: { label: 'Too short', color: '#E74C3C' },
    1: { label: 'Weak', color: '#E74C3C' },
    2: { label: 'Fair', color: '#F5A623' },
    3: { label: 'Good', color: '#4A90D9' },
    4: { label: 'Strong', color: '#2EAA4F' },
  }
  return { score, ...(map[score] || map[0]) }
})

function validate(): boolean {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (!form.name.trim()) errors.name = 'Name is required'
  if (form.password && form.password.length < 6) 
    errors.password = 'Password must be at least 6 characters'
  if (form.bio.length > 500)
    errors.bio = 'Bio must be under 500 characters'
  if (form.teachingPairs.length === 0) 
    errors.teachingPairs = 'Add at least one subject and level'
  return Object.keys(errors).length === 0
}

function handleFileUpload(event: any) {
  const file = event.target.files[0]
  if (!file) return
  form.profileImage = file
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const reader = new FileReader()
    reader.onload = (ev) => { avatarPreview.value = ev.target?.result as string }
    reader.readAsDataURL(input.files[0])
    form.photo = file
  }
}

async function addPair() {
  pairError.value = ''
  if (!newSubject.value || !newLevel.value) {
    pairError.value = 'Please select both a subject and a level'
    return
  }
  if (!newHourlyRate.value || newHourlyRate.value < 10) {
    pairError.value = 'Hourly rate must be at least $10'
    return
  }
  const exists = form.teachingPairs.some(
    (p: { subject: string; level: string }) => p.subject === newSubject.value && p.level === newLevel.value
  )
  if (exists) {
    pairError.value = 'This subject and level combination already exists'
    return
  }
  try {
    await addSubject(
      tutorId.value,
      newSubject.value,
      newLevel.value,
      newHourlyRate.value,
    );
    form.teachingPairs.push({ subject: newSubject.value, level: newLevel.value, hourlyRate: newHourlyRate.value })
  } catch (err: any) {
    pairError.value = (err.response?.data?.error || "Failed to add subject");
  }
  newSubject.value = ''
  newLevel.value = ''
  newHourlyRate.value = null
}

async function removePair(index: number) {
  const subjectId = form.teachingPairs[index].tutorSubjectId
  try {
    await deleteSubject(tutorId.value, subjectId)
    form.teachingPairs.splice(index, 1)
  } catch (err) {
    console.error("Failed to delete subject", err)
  }
}

async function saveProfile() {
  if (!validate()) return
  saving.value = true
  try {
    const formData = new FormData()
    formData.append("name", form.name)
    formData.append("phone", form.phone)
    formData.append("bio", form.bio)
    if (form.password) {
      formData.append("password", form.password)
    }
    if (form.profileImage) {
      formData.append("profileImage", form.profileImage)
    }
    const result = await updateProfile(tutorId.value, formData)
    const newImageURL = result?.data?.[0]?.imageURL
    if (newImageURL) {
      avatarPreview.value = newImageURL
      await user.value?.update({ unsafeMetadata: { ...user.value.unsafeMetadata, imageURL: newImageURL } })
    }
    originalData.value = JSON.stringify(normalizeForm())
    form.photo = null
    form.profileImage = null
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (err: any) {
    // Surface the actual API error to the user instead of silent failure
    const message = err?.response?.data?.error 
      || err?.response?.data?.message 
      || err?.message 
      || 'Failed to save profile. Please try again.'
    errors.general = message
    console.error('saveProfile error:', err)
  } finally {
    saving.value = false
  }
}

watch(activeTab, () => { saved.value = false })
</script>

<template>

  <div v-if="loading" class="text-center py-20">
  <div class="inline-block animate-spin">
    <svg class="w-8 h-8" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round"
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
    </svg>
  </div>
  <p class="mt-4" style="color:#1B3A5C">Loading tutor profile...</p>
  </div>

  <div v-else class="min-h-screen py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">

      <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Dashboard
      </router-link>

      <div class="rounded-2xl border overflow-hidden mb-6" style="background-color:#fff;border-color:#E8F0FE">
        <div class="p-6 md:p-8" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
          <div class="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            <div class="relative group">
              <img :src="avatarPreview" alt="Profile photo" class="w-20 h-20 rounded-2xl object-cover shadow-lg" crossorigin="anonymous" style="background-color:#E8F0FE"/>
              <label class="absolute inset-0 rounded-2xl flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer" style="background-color:rgba(27,58,92,0.6);transition:opacity 0.2s">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <circle cx="12" cy="13" r="3"/>
                </svg>
                <input type="file" accept="image/*" class="hidden" @change="handleFileUpload"/>
              </label>
            </div>
            <div>
              <h1 class="text-2xl font-extrabold text-white">Edit Profile</h1>
              <p class="text-sm mt-1" style="color:rgba(255,255,255,0.75)">{{ form.name }} · {{ form.email }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-2 mb-6 overflow-x-auto pb-1">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key" class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap" :style="{ backgroundColor: activeTab === tab.key ? '#4A90D9' : '#fff', color: activeTab === tab.key ? '#fff' : '#1B3A5C', border: activeTab === tab.key ? 'none' : '1px solid #E8F0FE', transition: 'all 0.2s' }">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" :d="tab.icon"/>
          </svg>
          {{ tab.label }}
        </button>
      </div>

      <div class="rounded-2xl border overflow-hidden" style="background-color:#fff;border-color:#E8F0FE">

        <div v-if="activeTab==='personal'" class="p-6 md:p-8 space-y-6">
          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Name</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-[25%]" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <input v-model="form.name" type="text" placeholder="Your full name" class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" :style="{ borderColor: errors.name ? '#E74C3C' : '#E8F0FE', color: '#1B3A5C' }"/>
            </div>
            <p v-if="errors.name" class="text-xs mt-1" style="color:#E74C3C">{{ errors.name }}</p>
          </div>

          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Email</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-[25%]" style="color:#4A90D9;opacity:0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <input :value="form.email" type="email" disabled class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border cursor-not-allowed" style="border-color:#E8F0FE;color:rgba(27,58,92,0.5);background-color:#F5F7FA"/>
            </div>
            <p class="text-xs mt-1" style="color:rgba(27,58,92,0.4)">Email cannot be changed. Contact support if you need to update it.</p>
          </div>

          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Phone Number</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-[25%]" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              <input v-model="form.phone" type="tel" placeholder="+65 9123 4567" class="w-full pl-11 pr-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" :style="{ borderColor: errors.phone ? '#E74C3C' : '#E8F0FE', color: '#1B3A5C' }"/>
            </div>
            <p v-if="errors.phone" class="text-xs mt-1" style="color:#E74C3C">{{ errors.phone }}</p>
          </div>

          <!-- <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Password</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-4 top-1/2 -translate-y-[25%]" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="Enter new password" class="w-full pl-11 pr-12 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" :style="{ borderColor: errors.password ? '#E74C3C' : '#E8F0FE', color: '#1B3A5C' }"/>
              <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-1/2 -translate-y-[25%] p-0.5" style="color:#4A90D9">
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="text-xs mt-1" style="color:#E74C3C">{{ errors.password }}</p>
            <div v-if="form.password" class="mt-2">
              <div class="flex gap-1.5 mb-1.5">
                <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full" :style="{ backgroundColor: i <= passwordStrength.score ? passwordStrength.color : '#E8F0FE', transition: 'background-color 0.3s' }"></div>
              </div>
              <p class="text-xs" :style="{ color: passwordStrength.color }">{{ passwordStrength.label }}</p>
            </div>
          </div> -->

          <div>
            <label class="text-sm font-bold block mb-2" style="color:#1B3A5C">Bio</label>
            <textarea v-model="form.bio" rows="4" placeholder="Tell students about yourself, your teaching philosophy, and what makes you a great tutor..." class="w-full px-4 py-3 rounded-xl text-sm border resize-none focus:outline-none focus:ring-2" :style="{ borderColor: errors.bio ? '#E74C3C' : '#E8F0FE', color: '#1B3A5C' }"></textarea>
            <div class="flex justify-between mt-1">
              <p v-if="errors.bio" class="text-xs" style="color:#E74C3C">{{ errors.bio }}</p>
              <p class="text-xs ml-auto" :style="{ color: form.bio.length > 500 ? '#E74C3C' : 'rgba(27,58,92,0.5)' }">{{ form.bio.length }}/500</p>
            </div>
          </div>

        </div>

        <div v-if="activeTab==='teaching'" class="p-6 md:p-8 space-y-6">

          <div class="rounded-xl p-5" style="background-color:#F5F7FA;border:1px solid #E8F0FE">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background-color:rgba(74,144,217,0.1)">
                <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
              </div>
              <p class="text-sm font-bold" style="color:#1B3A5C">Add Subject, Level &amp; Hourly Rate</p>
            </div>
            <div class="flex flex-col sm:flex-row gap-3">
              <div class="flex-1 relative">
                <select v-model="newSubject" class="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2 appearance-none cursor-pointer" :style="{ borderColor: '#E8F0FE', color: newSubject ? '#1B3A5C' : 'rgba(27,58,92,0.4)', backgroundColor: '#fff' }">
                  <option value="" disabled>Select subject</option>
                  <option v-for="subj in SUBJECTS" :key="subj" :value="subj">{{ subj }}</option>
                </select>
                <svg class="w-4 h-4 absolute right-4 top-1/2 -translate-y-[25%] pointer-events-none" style="color:rgba(27,58,92,0.3)" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
              <div class="flex-1 relative">
                <select v-model="newLevel" class="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2 appearance-none cursor-pointer" :style="{ borderColor: '#E8F0FE', color: newLevel ? '#1B3A5C' : 'rgba(27,58,92,0.4)', backgroundColor: '#fff' }">
                  <option value="" disabled>Select level</option>
                  <option v-for="lvl in LEVELS" :key="lvl" :value="lvl">{{ lvl }}</option>
                </select>
                <svg class="w-4 h-4 absolute right-4 top-1/2 -translate-y-[25%] pointer-events-none" style="color:rgba(27,58,92,0.3)" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
              <div class="w-full sm:w-32 relative">
                <span class="absolute left-4 top-1/2 -translate-y-[25%] text-sm font-bold" style="color:#4A90D9">$</span>
                <input v-model.number="newHourlyRate" type="number" min="10" step="5" placeholder="Rate" class="w-full pl-9 pr-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2" style="border-color:#E8F0FE;color:#1B3A5C;background-color:#fff"/>
              </div>
              <button :disabled="loading" @click="addPair" class="px-6 py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2 hover:opacity-90 shadow-sm" style="background-color:#4A90D9;white-space:nowrap">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                Add
              </button>
            </div>
            <p v-if="pairError" class="text-xs mt-2" style="color:#E74C3C">{{ pairError }}</p>
            <p v-if="errors.teachingPairs" class="text-xs mt-2" style="color:#E74C3C">{{ errors.teachingPairs }}</p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm font-bold" style="color:#1B3A5C">Your Subjects</p>
              <span v-if="form.teachingPairs.length > 0" class="text-xs font-semibold px-2.5 py-1 rounded-full" style="background-color:rgba(74,144,217,0.1);color:#4A90D9">{{ form.teachingPairs.length }} {{ form.teachingPairs.length === 1 ? 'entry' : 'entries' }}</span>
            </div>

            <div v-if="form.teachingPairs.length > 0" class="space-y-2">
              <div v-for="(pair, idx) in form.teachingPairs" :key="idx" class="flex items-center justify-between px-4 py-3.5 rounded-xl" style="background-color:#fff;border:1px solid #E8F0FE;transition:all 0.15s">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background-color:rgba(74,144,217,0.08)">
                    <svg class="w-4 h-4" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold" style="color:#1B3A5C">{{ pair.subject }}</p>
                    <p class="text-xs" style="color:rgba(27,58,92,0.5)">{{ pair.level }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-sm font-bold" style="color:#2EAA4F">${{ pair.hourlyRate }}/hr</span>
                  <button @click="removePair(idx)" class="w-8 h-8 rounded-lg flex items-center justify-center hover:opacity-80" style="background-color:rgba(231,76,60,0.06);transition:all 0.15s" title="Remove">
                    <svg class="w-4 h-4" style="color:#E74C3C" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div v-else class="flex flex-col items-center justify-center py-12 rounded-xl" style="background-color:#F5F7FA;border:1px dashed rgba(27,58,92,0.15)">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center mb-3" style="background-color:rgba(74,144,217,0.08)">
                <svg class="w-6 h-6" style="color:rgba(27,58,92,0.2)" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                </svg>
              </div>
              <p class="text-sm font-semibold" style="color:rgba(27,58,92,0.4)">No subjects added yet</p>
              <p class="text-xs mt-1" style="color:rgba(27,58,92,0.3)">Use the form above to add your first subject</p>
            </div>
          </div>

        </div>

        <div v-if="activeTab === 'personal'" class="px-6 md:px-8 py-5 flex flex-col sm:flex-row items-center justify-between gap-4" style="border-top:1px solid #E8F0FE;background-color:#FAFBFC">
          <div v-if="isDirty" class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" style="background-color:#F5A623"></span>
            <p class="text-xs font-medium" style="color:#1B3A5C;opacity:0.6">You have unsaved changes</p>
          </div>
          <div v-else></div>
          <div class="flex items-center gap-3">
            <router-link to="/dashboard" class="px-6 py-3 rounded-xl text-sm font-semibold" style="color:#1B3A5C;background-color:#F5F7FA;border:1px solid #E8F0FE">Cancel</router-link>
            <button @click="saveProfile" :disabled="saving || !isDirty" class="px-8 py-3 rounded-xl text-sm font-bold text-white shadow-md hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2" style="background-color:#4A90D9">
              <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
      <!-- <button @click="console.log('test')">Test Click</button> -->

      <div v-if="saved" class="fixed bottom-6 right-6 flex items-center gap-3 px-5 py-4 rounded-xl shadow-lg" style="background-color:#fff;border:1px solid #E8F0FE;z-index:50">
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
  <p v-if="errors.general" class="text-xs text-center" style="color:#E74C3C">
  {{ errors.general }}
</p>
</template>
