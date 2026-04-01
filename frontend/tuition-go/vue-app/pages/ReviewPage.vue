<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { StarRating } from "../components";
import { useSessionService } from "../services/sessionService";
import { useApi } from "../services/api";

function fmtDate(d: string) {
  return new Date(d + 'Z').toLocaleDateString("en-SG", {
    weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC"
  });
}

function fmtTime(d: string) {
  return new Date(d + 'Z').toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" });
}

const route = useRoute();
const sessionService = useSessionService();
const api = useApi();

const sessionId = route.params.sessionId as string;

const rating = ref(0);
const comment = ref("");
const submitted = ref(false);
const isSubmitting = ref(false);
const error = ref("");
const loadError = ref("");
const session = ref<any>(null);
const loading = ref(true);
const alreadyReviewed = ref(false);

const ratingLabel = computed(() => {
  const l: Record<number, string> = { 1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent" };
  return l[rating.value] || "";
});

onMounted(async () => {
  try {
    const { data } = await sessionService.getSessionById(sessionId)
    if (data.status !== 'completed') {
      loadError.value = "You can only review completed sessions."
      return
    }
    session.value = data

    // Check for duplicate review
    try {
      const { data: tutorData } = await api.get(`/get-tutor/${data.tutorId}`)
      const reviews: any[] = tutorData?.reviews ?? []
      if (reviews.some((r: any) => r.session_id === sessionId)) {
        alreadyReviewed.value = true
      }
    } catch {
      // Non-fatal: if check fails, still show form
    }
  } catch {
    loadError.value = "Session not found."
  } finally {
    loading.value = false
  }
})

async function submitReview() {
  if (!session.value || !rating.value || !comment.value.trim()) return;
  isSubmitting.value = true;
  error.value = "";

  try {
    await api.post("/rate-tutor/review", {
      session_id: sessionId,
      tutor_id: session.value.tutorId,
      rating: rating.value,
      comment: comment.value.trim(),
    });
    submitted.value = true;
  } catch (e: any) {
    error.value = e?.response?.data?.message || e.message || "Something went wrong. Please try again.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="py-8 md:py-12" style="background-color: #f5f7fa">
    <div class="max-w-xl mx-auto px-4 sm:px-6 lg:px-8">

      <router-link to="/dashboard" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color: #4a90d9">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Dashboard
      </router-link>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <svg class="animate-spin w-8 h-8 mx-auto" style="color:#4A90D9" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </div>

      <!-- Load error -->
      <div v-else-if="loadError" class="text-center py-20 rounded-2xl border p-8" style="background-color:#fff;border-color:#E8F0FE">
        <p class="text-base font-semibold mb-4" style="color:#E74C3C">{{ loadError }}</p>
        <router-link to="/dashboard" class="inline-block px-6 py-2 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">Back to Dashboard</router-link>
      </div>

      <!-- Already reviewed -->
      <div v-else-if="alreadyReviewed" class="rounded-2xl border p-8 text-center" style="background-color:#fff;border-color:#E8F0FE">
        <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style="background-color:rgba(74,144,217,0.1)">
          <svg class="w-10 h-10" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-extrabold mb-2" style="color:#1B3A5C">Already Reviewed</h2>
        <p class="text-sm mb-6" style="color:#1B3A5C;opacity:0.7">You have already submitted a review for this session.</p>
        <router-link to="/dashboard" class="inline-block px-8 py-3 rounded-xl text-sm font-semibold text-white" style="background-color:#4A90D9">
          Back to Dashboard
        </router-link>
      </div>

      <!-- Review form -->
      <div v-else-if="session && !submitted" class="rounded-2xl border overflow-hidden" style="background-color: #fff; border-color: #e8f0fe">
        <div class="p-6" style="background: linear-gradient(135deg, #1b3a5c 0%, #4a90d9 100%)">
          <h1 class="text-2xl font-extrabold text-white">Leave a Review</h1>
          <p class="text-sm mt-1" style="color: rgba(255, 255, 255, 0.75)">Share your experience with {{ session.tutorName }}</p>
        </div>
        <div class="p-6 space-y-6">
          <!-- Session summary -->
          <div class="flex items-center gap-4 p-4 rounded-xl" style="background-color: #f5f7fa">
            <img
              :src="session.tutorImageUrl || 'https://api.dicebear.com/9.x/notionists/svg?seed=' + session.tutorId"
              :alt="session.tutorName"
              class="w-14 h-14 rounded-xl object-cover"
              crossorigin="anonymous"
              style="background-color: #e8f0fe"
            />
            <div>
              <p class="font-bold" style="color: #1b3a5c">{{ session.tutorName }}</p>
              <p class="text-sm" style="color: #4a90d9">{{ session.subjectName }} ({{ session.academicLevel }})</p>
              <p class="text-xs mt-0.5" style="color: #1b3a5c; opacity: 0.6">
                {{ fmtDate(session.startTime) }} · {{ fmtTime(session.startTime) }} – {{ fmtTime(session.endTime) }}
              </p>
            </div>
          </div>

          <!-- Star rating -->
          <div>
            <label class="text-sm font-bold block mb-3" style="color: #1b3a5c">How would you rate this session?</label>
            <div class="flex items-center gap-4">
              <StarRating v-model:modelValue="rating" :interactive="true" size="lg"/>
              <span v-if="rating" class="text-lg font-bold" style="color: #1b3a5c">{{ ratingLabel }}</span>
            </div>
          </div>

          <!-- Comment -->
          <div>
            <label class="text-sm font-bold block mb-2" style="color: #1b3a5c">Your review</label>
            <textarea
              v-model="comment"
              rows="5"
              maxlength="500"
              placeholder="Tell others about your experience..."
              class="w-full px-4 py-3 rounded-xl text-sm border resize-none focus:outline-none focus:ring-2"
              style="border-color: #e8f0fe; color: #1b3a5c"
            ></textarea>
            <p class="text-xs mt-1 text-right" style="color: #1b3a5c; opacity: 0.5">{{ comment.length }}/500</p>
          </div>

          <p v-if="error" class="text-sm text-red-500 text-center">{{ error }}</p>

          <button
            @click="submitReview"
            :disabled="!rating || !comment.trim() || isSubmitting"
            class="w-full py-4 rounded-xl text-base font-bold text-white hover:opacity-90 shadow-md disabled:opacity-40 disabled:cursor-not-allowed"
            style="background-color: #4a90d9"
          >
            {{ isSubmitting ? "Submitting..." : "Submit Review" }}
          </button>
        </div>
      </div>

      <!-- Success -->
      <div v-if="submitted" class="rounded-2xl border p-8 text-center" style="background-color: #fff; border-color: #e8f0fe">
        <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style="background-color: rgba(46, 170, 79, 0.1)">
          <svg class="w-10 h-10" style="color: #2eaa4f" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-extrabold mb-2" style="color: #1b3a5c">Review Submitted!</h2>
        <p class="text-sm mb-6" style="color: #1b3a5c; opacity: 0.7">Thank you for your feedback. Your review helps other students find great tutors.</p>
        <router-link to="/dashboard" class="inline-block px-8 py-3 rounded-xl text-sm font-semibold text-white" style="background-color: #4a90d9">
          Back to Dashboard
        </router-link>
      </div>

    </div>
  </div>
</template>
