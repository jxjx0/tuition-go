<script setup lang="ts">
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'

const router = useRouter()
const { user } = useUser()

watch(() => user.value, (u) => {
  if (!u) return
  const role = u.unsafeMetadata?.role
  router.replace(role === 'tutor' ? '/tutor-dashboard' : '/dashboard')
}, { immediate: true })
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center">
    <div class="animate-spin w-8 h-8 border-4 rounded-full" style="border-color:#E8F0FE;border-top-color:#4A90D9"></div>
  </div>
</template>
