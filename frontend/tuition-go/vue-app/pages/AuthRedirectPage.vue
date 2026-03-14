<script setup lang="ts">
import { watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'
import { useStudentService } from '../services/studentService'

const router = useRouter()
const { user } = useUser()
const error = ref<string | null>(null)

// Call at setup level so useAuth() inside runs in the right context
const studentService = useStudentService()

async function registerStudentIfNeeded(u: NonNullable<typeof user.value>): Promise<boolean> {
  const metadata = u.unsafeMetadata as Record<string, unknown>

  // Already registered — nothing to do
  if (metadata?.studentId) return true

  try {
    const response = await studentService.register({
      name: u.fullName ?? u.firstName ?? 'Student',
      email: u.primaryEmailAddress?.emailAddress ?? '',
      clerkUserId: u.id,
    })

    const studentId: string = response.data.studentId

    // Persist studentId back into Clerk so every page can read it
    await u.update({
      unsafeMetadata: {
        ...metadata,
        role: 'student',
        studentId,
      },
    })

    return true
  } catch (err: any) {
    console.error('Student registration failed:', err)
    error.value = 'Failed to set up your student profile. Please refresh and try again.'
    return false
  }
}

watch(
  () => user.value,
  async (u) => {
    if (!u) return

    const role = (u.unsafeMetadata as Record<string, unknown>)?.role

    if (role === 'tutor') {
      router.replace('/tutor-dashboard')
      return
    }

    // Student flow: ensure record exists in DB before navigating
    const ok = await registerStudentIfNeeded(u)
    if (ok) {
      router.replace('/dashboard')
    }
    // If not ok, error message is shown and user stays on page to retry
  },
  { immediate: true },
)
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center gap-4">
    <div
      v-if="!error"
      class="animate-spin w-8 h-8 border-4 rounded-full"
      style="border-color:#E8F0FE;border-top-color:#4A90D9"
    />
    <div v-else class="text-center space-y-3">
      <p class="text-sm font-medium" style="color:#ef4444">{{ error }}</p>
      <button
        @click="error = null; registerStudentIfNeeded(user!).then(ok => { if (ok) router.replace('/dashboard') })"
        class="px-5 py-2 rounded-xl text-sm font-semibold text-white"
        style="background-color:#4A90D9"
      >
        Retry
      </button>
    </div>
  </div>
</template>
