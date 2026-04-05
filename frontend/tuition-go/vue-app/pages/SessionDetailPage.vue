<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useUser } from "@clerk/vue";
import { useSessionService } from "../services/sessionService";
import { useApi } from "../services/api";
import { avatarUrl } from "../utils/avatar";

interface Session {
  id: string;
  tutorId: string;
  studentId: string;
  studentAvatar: string;
  tutorSubjectId: string;
  startTime: string;
  endTime: string;
  status: string;
  durationMins: number;
  meetingLink: string;
  createdAt: string;
  updatedAt: string;
  tutorName: string;
  tutorAvatar: string;
  subject: string;
  level: string;
  date: string;
  price: number;
  notes?: string;
  review?: {
    review_id: string;
    rating: number;
    comment: string;
    createdAt: string;
  } | null;
}

function toUtcDate(d: string) {
  return new Date(d + "Z");
}

function fmtDate(d: string) {
  return toUtcDate(d).toLocaleDateString("en-SG", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

function fmtTime(d: string) {
  return toUtcDate(d).toLocaleTimeString("en-SG", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

const route = useRoute();
const router = useRouter();
const { user } = useUser();
const session = ref<Session | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const showCancel = ref(false);
const cancelling = ref(false);
const cancelledSuccess = ref(false);
const cancelError = ref<string | null>(null);
const sessionService = useSessionService();
const api = useApi();
const booking = ref(false);

async function bookSession() {
  if (!session.value || !currentStudentId.value) return;
  booking.value = true;
  try {
    const { data } = await api.post("/checkout/checkout", {
      session_id: session.value.id,
      student_id: currentStudentId.value,
    });
    window.location.href = data.url;
  } catch (err: any) {
    const msg = err?.response?.data?.message;
    error.value = msg || "Failed to initiate booking. Please try again.";
    console.error("Failed to initiate booking", err);
    booking.value = false;
  }
}

const metadata = computed(
  () => user.value?.unsafeMetadata as Record<string, unknown> | undefined,
);
const currentStudentId = computed(() =>
  typeof metadata.value?.studentId === "string"
    ? metadata.value.studentId
    : null,
);
const userRole = computed(() =>
  typeof metadata.value?.role === "string" ? metadata.value.role : null,
);

const isOwner = computed(
  () =>
    session.value?.status === "available" ||
    userRole.value === "tutor" ||
    session.value?.studentId === currentStudentId.value,
);

const statusLabel = computed(() => {
  if (!session.value) return "";
  const m: Record<string, string> = {
    available: "Available",
    booked: "Upcoming",
    completed: "Completed",
    cancelled: "Cancelled",
  };
  return m[session.value.status] || session.value.status;
});

const canCancel = computed(() => {
  if (!session.value || session.value.status !== "booked") return false;
  const now = new Date();
  const startSgt = toUtcDate(session.value.startTime);
  const startUtc = new Date(startSgt.getTime() - 8 * 60 * 60 * 1000);
  const diffHours = (startUtc.getTime() - now.getTime()) / (1000 * 60 * 60);
  return diffHours >= 2;
});

const headerStyle = computed(() => {
  if (!session.value) return "";
  if (session.value.status === "completed")
    return "background:linear-gradient(135deg,#1a6b36 0%,#2EAA4F 100%)";
  if (session.value.status === "cancelled")
    return "background:linear-gradient(135deg,#991b1b 0%,#ef4444 100%)";
  return "background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)";
});

async function fetchSession() {
  try {
    loading.value = true;
    error.value = null;
    const sessionId = route.params.id as string;
    const { data } = await sessionService.getSessionById(sessionId);

    session.value = {
      id: data.sessionId,
      tutorId: data.tutorId,
      studentId: data.studentId,
      studentAvatar: avatarUrl(data.studentImageUrl, data.studentId),
      tutorSubjectId: data.tutorSubjectId,
      startTime: data.startTime,
      endTime: data.endTime,
      status: data.status,
      durationMins: data.durationMins,
      meetingLink: data.meetingLink,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      tutorName: data.tutorName,
      tutorAvatar: avatarUrl(data.tutorImageUrl, data.tutorId),
      subject: data.subjectName,
      level: data.academicLevel,
      date: data.startTime,
      price: data.totalPrice,
      review: data.review ?? null,
    };
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = "Session not found";
    } else {
      error.value = "Failed to load session";
    }
    console.error("Failed to fetch session:", err);
  } finally {
    loading.value = false;
  }
}

async function cancelSession() {
  if (!session.value || !currentStudentId.value) return;
  cancelling.value = true;
  cancelError.value = null;
  try {
    await sessionService.cancelSession(
      session.value.id,
      currentStudentId.value,
    );
    cancelledSuccess.value = true;
    showCancel.value = false;
  } catch (err: any) {
    const msg =
      err.response?.data?.message ||
      "Failed to cancel session. Please try again.";
    cancelError.value = msg;
  } finally {
    cancelling.value = false;
  }
}

function isWithinReviewWindow(sessionDate: string): boolean {
  const diffDays =
    (Date.now() - new Date(sessionDate).getTime()) / (1000 * 60 * 60 * 24);
  return diffDays <= 14;
}

onMounted(() => {
  fetchSession();
});
</script>

<template>
  <div class="py-8 md:py-12" style="background-color: #f5f7fa">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <router-link
        to="/dashboard"
        class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80"
        style="color: #4a90d9"
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to Dashboard
      </router-link>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <svg
          class="animate-spin w-8 h-8 mx-auto"
          style="color: #4a90d9"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-20">
        <h2 class="text-2xl font-bold" style="color: #ef4444">{{ error }}</h2>
        <router-link
          to="/dashboard"
          class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white"
          style="background-color: #4a90d9"
          >Back to Dashboard</router-link
        >
      </div>

      <!-- Not authorised -->
      <div v-else-if="!isOwner" class="text-center py-20">
        <h2 class="text-xl font-bold" style="color: #e74c3c">
          You are not authorised to view this session.
        </h2>
        <router-link
          to="/dashboard"
          class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white"
          style="background-color: #4a90d9"
          >Back to Dashboard</router-link
        >
      </div>

      <!-- Cancellation success -->
      <div
        v-else-if="cancelledSuccess"
        class="rounded-2xl border p-12 text-center"
        style="background-color: #fff; border-color: #e8f0fe"
      >
        <div
          class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <svg
            class="w-10 h-10 text-green-600"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 class="text-3xl font-extrabold mb-4" style="color: #1b3a5c">
          Cancellation Confirmed
        </h2>
        <p class="text-lg mb-8" style="color: #1b3a5c; opacity: 0.7">
          Your session has been successfully cancelled and a full refund has
          been initiated.
        </p>
        <router-link
          to="/dashboard"
          class="inline-block px-8 py-4 rounded-xl text-lg font-bold text-white hover:opacity-90"
          style="background-color: #4a90d9"
          >Return to Dashboard</router-link
        >
      </div>

      <!-- Session detail -->
      <div
        v-else-if="session"
        class="rounded-2xl border overflow-hidden"
        style="background-color: #fff; border-color: #e8f0fe"
      >
        <!-- Header -->
        <div class="p-6" :style="headerStyle">
          <span
            class="px-3 py-1 rounded-full text-xs font-bold mb-3 inline-block"
            style="background-color: rgba(255, 255, 255, 0.2); color: #fff"
            >{{ statusLabel }}</span
          >
          <h1 class="text-2xl font-extrabold text-white">
            {{ session.subject }} ({{ session.level }})
          </h1>
          <p class="text-sm mt-1" style="color: rgba(255, 255, 255, 0.75)">
            Session with {{ session.tutorName }}
          </p>
        </div>

        <div class="p-6 space-y-6">
          <!-- Tutor card -->
          <div
            class="flex items-center gap-4 p-4 rounded-xl"
            style="background-color: #f5f7fa"
          >
            <img
              :src="session.tutorAvatar"
              :alt="session.tutorName"
              class="w-14 h-14 rounded-xl"
              crossorigin="anonymous"
              style="background-color: #e8f0fe"
            />
            <div class="flex-1">
              <p class="font-bold" style="color: #1b3a5c">
                {{ session.tutorName }}
              </p>
              <router-link
                :to="'/tutors/' + session.tutorId"
                class="text-xs font-medium hover:underline"
                style="color: #4a90d9"
                >View Profile</router-link
              >
            </div>
            <p class="text-xl font-extrabold" style="color: #2eaa4f">
              ${{ session.price.toFixed(2) }}
            </p>
          </div>

          <!-- Date & time -->
          <div
            class="rounded-xl p-4 space-y-3"
            style="background-color: #f5f7fa; border: 1px solid #e8f0fe"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                style="background-color: #e8f0fe"
              >
                <svg
                  class="w-4 h-4"
                  style="color: #4a90d9"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div>
                <p
                  class="text-xs font-semibold uppercase mb-0.5"
                  style="color: #1b3a5c; opacity: 0.4"
                >
                  Date
                </p>
                <p class="text-sm font-bold" style="color: #1b3a5c">
                  {{ fmtDate(session.date) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div
                class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                style="background-color: #e8f0fe"
              >
                <svg
                  class="w-4 h-4"
                  style="color: #4a90d9"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <p
                  class="text-xs font-semibold uppercase mb-0.5"
                  style="color: #1b3a5c; opacity: 0.4"
                >
                  Time
                </p>
                <p class="text-sm font-bold" style="color: #1b3a5c">
                  {{ fmtTime(session.startTime) }} –
                  {{ fmtTime(session.endTime) }}
                  <span class="font-normal" style="color: #1b3a5c; opacity: 0.5"
                    >· {{ session.durationMins }} mins</span
                  >
                </p>
              </div>
            </div>
          </div>

          <!-- Session notes -->
          <div
            v-if="session.notes"
            class="p-4 rounded-xl"
            style="background-color: #f5f7fa"
          >
            <p class="text-xs font-semibold mb-1" style="color: #1b3a5c">
              Session Notes
            </p>
            <p class="text-sm" style="color: #1b3a5c; opacity: 0.8">
              {{ session.notes }}
            </p>
          </div>

          <!-- Meeting link -->
          <div
            v-if="session.meetingLink && session.status === 'booked'"
            class="p-4 rounded-xl border"
            style="border-color: #e8f0fe"
          >
            <p class="text-xs font-semibold mb-2" style="color: #1b3a5c">
              Google Meet
            </p>
            <a
              :href="session.meetingLink"
              target="_blank"
              class="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90"
              style="background-color: #2eaa4f"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              Join Meeting
            </a>
          </div>

          <!-- Action buttons row — buttons only -->
          <div class="flex flex-col sm:flex-row gap-3">
            <!-- Book Session -->
            <button
              v-if="session.status === 'available' && userRole !== 'tutor'"
              @click="bookSession"
              :disabled="booking"
              class="flex-1 py-3 rounded-xl text-sm font-bold text-white hover:opacity-90 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              style="background-color: #2eaa4f"
            >
              <svg
                v-if="booking"
                class="animate-spin w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              {{ booking ? "Processing..." : "Book Session" }}
            </button>

            <!-- Cancel Session -->
            <button
              v-if="
                session.status === 'booked' &&
                !showCancel &&
                userRole === 'student'
              "
              @click="showCancel = true"
              :disabled="!canCancel"
              :class="[
                !canCancel
                  ? 'opacity-50 cursor-not-allowed grayscale'
                  : 'hover:bg-red-50',
              ]"
              class="flex-1 py-3 rounded-xl text-sm font-semibold border"
              style="border-color: #ef4444; color: #ef4444"
            >
              {{
                canCancel ? "Cancel Session" : "Cancellation Unavailable (< 2h)"
              }}
            </button>

            <!-- Leave a Review (no review yet, within window) -->
            <router-link
              v-if="
                session.status === 'completed' &&
                userRole === 'student' &&
                !session.review &&
                isWithinReviewWindow(session.date)
              "
              :to="'/review/' + session.id"
              class="flex-1 py-3 rounded-xl text-sm font-semibold text-white text-center hover:opacity-90"
              style="background-color: #4a90d9"
            >
              Leave a Review
            </router-link>

            <!-- Review window closed (no review, past 14 days) -->
            <p
              v-if="
                session.status === 'completed' &&
                userRole === 'student' &&
                !session.review &&
                !isWithinReviewWindow(session.date)
              "
              class="text-xs text-center py-2"
              style="color: #1b3a5c; opacity: 0.45"
            >
              Review window has closed (14 days)
            </p>
          </div>

          <!-- Existing review card — outside button row -->
          <div
            v-if="
              session.status === 'completed' &&
              userRole === 'student' &&
              session.review
            "
            class="p-4 rounded-xl border"
            style="border-color: #e8f0fe; background-color: #f5f7fa"
          >
            <div class="flex items-center justify-between mb-2">
              <p
                class="text-xs font-semibold uppercase"
                style="color: #1b3a5c; opacity: 0.5"
              >
                Your Review
              </p>
              <!-- Edit button — only within 14-day window -->
              <router-link
                v-if="isWithinReviewWindow(session.date)"
                :to="'/review/' + session.id"
                class="text-xs font-semibold px-3 py-1 rounded-lg hover:opacity-80"
                style="background-color: #e8f0fe; color: #4a90d9"
              >
                Update Review
              </router-link>
            </div>
            <!-- Reviewer row: avatar + stars + comment stacked properly -->
            <div class="flex items-center gap-3">
              <!-- Avatar — unchanged -->
              <img
                :src="session.studentAvatar"
                class="w-14 h-14 rounded-xl flex-shrink-0"
                crossorigin="anonymous"
                style="background-color: #e8f0fe"
              />

              <div class="flex flex-col justify-center gap-1">
                <!-- Stars -->
                <div class="flex items-center gap-0.5">
                  <template v-for="i in 5" :key="i">
                    <svg
                      class="w-4 h-4"
                      :style="
                        i <= session.review.rating
                          ? 'color:#F59E0B'
                          : 'color:#E8F0FE'
                      "
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                      />
                    </svg>
                  </template>
                </div>

                <!-- Comment -->
                <p class="text-sm" style="color: #1b3a5c; opacity: 0.8">
                  {{ session.review.comment }}
                </p>
              </div>
            </div>
          </div>

          <!-- Cancel confirm dialog -->
          <div
            v-if="showCancel"
            class="p-5 rounded-xl border"
            style="
              border-color: #ef4444;
              background-color: rgba(239, 68, 68, 0.03);
            "
          >
            <p class="text-sm font-bold mb-1" style="color: #ef4444">
              Cancel this session?
            </p>
            <p class="text-xs mb-4" style="color: #1b3a5c; opacity: 0.7">
              A full refund will be processed within 3-5 business days.
            </p>
            <div
              v-if="cancelError"
              class="mb-3 p-3 rounded-lg text-xs font-medium"
              style="background-color: rgba(239, 68, 68, 0.08); color: #ef4444"
            >
              {{ cancelError }}
            </div>
            <div class="flex gap-3">
              <button
                @click="cancelSession"
                :disabled="cancelling"
                class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                style="background-color: #ef4444"
              >
                <svg
                  v-if="cancelling"
                  class="animate-spin w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  />
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                {{ cancelling ? "Cancelling..." : "Yes, Cancel" }}
              </button>
              <button
                @click="
                  showCancel = false;
                  cancelError = null;
                "
                :disabled="cancelling"
                class="px-6 py-2.5 rounded-xl text-sm font-semibold border disabled:opacity-60"
                style="border-color: #e8f0fe; color: #1b3a5c"
              >
                Keep Session
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Session not found -->
      <div v-else class="text-center py-20">
        <h2 class="text-2xl font-bold" style="color: #1b3a5c">
          Session not found
        </h2>
        <router-link
          to="/dashboard"
          class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white"
          style="background-color: #4a90d9"
          >Back to Dashboard</router-link
        >
      </div>
    </div>
  </div>
</template>
