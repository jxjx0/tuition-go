<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useUser } from "@clerk/vue";
import { useSessionService } from "../services/sessionService";
import { avatarUrl } from "../utils/avatar";

interface Session {
  id: string;
  tutorId: string;
  tutorName: string;
  tutorAvatar: string;
  subject: string;
  level: string;
  date: string;
  startTime: string;
  endTime: string;
  price: number;
  status: string;
  meetingLink: string | null;
  notes: string | null;
  durationMins: number;
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-SG", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function fmtTime(d: string) {
  return new Date(d).toLocaleTimeString("en-SG", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

const activeTab = ref("upcoming");
const { user, isLoaded } = useUser();
const currentStudentId = computed(() => {
  const metadata = user.value?.unsafeMetadata as
    | Record<string, unknown>
    | undefined;
  return typeof metadata?.studentId === "string" ? metadata.studentId : null;
});

const sessions = ref<Session[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const sessionService = useSessionService();

const fetchSessions = async () => {
  if (!currentStudentId.value) {
    sessions.value = [];
    error.value = "Student profile is not linked to this account yet.";
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    const { data } = await sessionService.getStudentSessions(
      currentStudentId.value,
    );
    sessions.value = data.map((session: any) => ({
      id: session.sessionId,
      tutorId: session.tutorId,
      tutorName: session.tutorName || "Unknown Tutor",
      tutorAvatar: avatarUrl(session.tutorImageUrl, session.tutorId),
      subject: session.subjectName || "Unknown Subject",
      level: session.academicLevel || "Unknown",
      date: session.startTime,
      startTime: fmtTime(session.startTime),
      endTime: fmtTime(session.endTime),
      price: session.totalPrice || 0,
      status: session.status || "pending",
      meetingLink: session.meetingLink,
      notes: null,
      durationMins: session.durationMins || 0,
    }));
  } catch (err: any) {
    if (err.response?.status === 404) {
      sessions.value = [];
      return;
    }
    error.value = err.message;
    console.error("Error fetching sessions:", err);
    sessions.value = [];
  } finally {
    loading.value = false;
  }
};

const upcomingSessions = computed(() =>
  sessions.value
    .filter((s) => s.status === "booked")
    .sort(
      (a: any, b: any) =>
        new Date(a.date).getTime() - new Date(b.date).getTime(),
    ),
);
const completedSessions = computed(() =>
  sessions.value
    .filter((s) => s.status === "completed")
    .sort(
      (a: any, b: any) =>
        new Date(b.date).getTime() - new Date(a.date).getTime(),
    ),
);

const tabs = computed(() => [
  { key: "upcoming", label: "Upcoming", count: upcomingSessions.value.length },
  {
    key: "completed",
    label: "Completed",
    count: completedSessions.value.length,
  },
]);

const displayedSessions = computed(() => {
  if (activeTab.value === "completed") return completedSessions.value;
  return upcomingSessions.value;
});

watch(
  () => [isLoaded.value, currentStudentId.value],
  ([loaded, studentId]) => {
    if (loaded && studentId) fetchSessions();
  },
  { immediate: true },
);


function isWithinReviewWindow(sessionDate: string): boolean {
  const session = new Date(sessionDate);
  const now = new Date();
  const diffMs = now.getTime() - session.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);
  return diffDays <= 14;
}
</script>

<template>
  <div class="py-8 md:py-12" style="background-color: #f5f7fa">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div
        class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-10"
      >
        <div>
          <h1 class="text-3xl font-extrabold" style="color: #1b3a5c">
            Welcome back, {{ user?.firstName ?? "Student" }}
          </h1>
          <p class="mt-1 text-base" style="color: #1b3a5c; opacity: 0.6">
            Here is a summary of your learning journey
          </p>
        </div>
        <router-link
          to="/tutors"
          class="px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-sm hover:opacity-90"
          style="background-color: #4a90d9"
          >Book New Session</router-link
        >
      </div>


      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin">
          <svg
            class="w-8 h-8"
            style="color: #4a90d9"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </div>
        <p class="mt-4" style="color: #1b3a5c">Loading your sessions...</p>
      </div>
      <div
        v-else-if="error"
        class="text-center py-20 rounded-2xl border p-8"
        style="background-color: #fff; border-color: #e8f0fe"
      >
        <h2 class="text-xl font-bold mb-2" style="color: #ef4444">
          Error loading sessions
        </h2>
        <p class="mb-4" style="color: #1b3a5c; opacity: 0.7">{{ error }}</p>
        <button
          @click="fetchSessions"
          class="px-6 py-2 rounded-xl text-sm font-semibold text-white"
          style="background-color: #4a90d9"
        >
          Try Again
        </button>
      </div>
      <div
        v-else-if="sessions.length === 0"
        class="text-center py-20 rounded-2xl border p-8"
        style="background-color: #fff; border-color: #e8f0fe"
      >
        <h2 class="text-xl font-bold mb-2" style="color: #1b3a5c">
          No sessions yet
        </h2>
        <p class="mb-4" style="color: #1b3a5c; opacity: 0.7">
          Start your learning journey by booking a session with a tutor
        </p>
        <router-link
          to="/tutors"
          class="inline-block px-6 py-2 rounded-xl text-sm font-semibold text-white"
          style="background-color: #4a90d9"
          >Browse Tutors</router-link
        >
      </div>
      <div v-else>
        <!-- Tab bar -->
        <div
          class="flex items-center gap-1 p-1 rounded-xl mb-6"
          style="background-color: #e8f0fe"
        >
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            class="flex-1 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all"
            :style="
              activeTab === tab.key
                ? 'background-color:#fff;color:#4A90D9;box-shadow:0 1px 3px rgba(0,0,0,0.08)'
                : 'color:#1B3A5C;opacity:0.7'
            "
          >
            {{ tab.label }} ({{ tab.count }})
          </button>
        </div>

        <!-- Session cards -->
        <div class="space-y-4">
          <div
            v-for="session in displayedSessions"
            :key="session.id"
            class="rounded-2xl border p-5 hover:shadow-sm"
            :class="session.status === 'cancelled' ? 'opacity-60' : ''"
            style="background-color: #fff; border-color: #e8f0fe"
          >
            <div class="flex flex-col sm:flex-row items-start gap-4">
              <img
                :src="session.tutorAvatar"
                :alt="session.tutorName"
                class="w-14 h-14 rounded-xl object-cover flex-shrink-0"
                crossorigin="anonymous"
                style="background-color: #e8f0fe"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="text-base font-bold" style="color: #1b3a5c">
                    {{ session.subject }} ({{ session.level }})
                  </h3>
                  <span
                    class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
                    :style="
                      session.status === 'completed'
                        ? 'background-color:rgba(46,170,79,0.1);color:#2EAA4F'
                        : session.status === 'cancelled'
                          ? 'background-color:rgba(239,68,68,0.1);color:#ef4444'
                          : 'background-color:#E8F0FE;color:#4A90D9'
                    "
                    >{{
                      session.status === "completed"
                        ? "Completed"
                        : session.status === "cancelled"
                          ? "Cancelled"
                          : "Upcoming"
                    }}</span
                  >
                </div>
                <p class="text-sm mt-1" style="color: #1b3a5c; opacity: 0.7">
                  with {{ session.tutorName }}
                </p>
                <div
                  class="flex flex-wrap items-center gap-4 mt-3 text-xs"
                  style="color: #1b3a5c; opacity: 0.6"
                >
                  <span>{{ fmtDate(session.date) }}</span>
                  <span>{{ session.startTime }} - {{ session.endTime }}</span>
                  <span class="font-semibold" style="color: #2eaa4f"
                    >${{ session.price.toFixed(2) }}</span
                  >
                </div>
                <p
                  v-if="session.notes"
                  class="mt-2 text-xs px-3 py-1.5 rounded-lg"
                  style="
                    background-color: #f5f7fa;
                    color: #1b3a5c;
                    opacity: 0.7;
                  "
                >
                  {{ session.notes }}
                </p>
              </div>
              <div class="flex flex-row sm:flex-col gap-2 flex-shrink-0">
                <a
                  v-if="session.meetingLink && session.status === 'booked'"
                  :href="session.meetingLink"
                  target="_blank"
                  class="px-4 py-2 rounded-xl text-xs font-semibold text-white text-center hover:opacity-90"
                  style="background-color: #2eaa4f"
                  >Join Meeting</a
                >
                <router-link
                  :to="'/session/' + session.id"
                  class="px-4 py-2 rounded-xl text-xs font-semibold text-center border hover:bg-gray-50"
                  style="border-color: #e8f0fe; color: #4a90d9"
                  >Details</router-link
                >
                <router-link
                  v-if="
                    session.status === 'completed' &&
                    isWithinReviewWindow(session.date)
                  "
                  :to="'/review/' + session.id"
                  class="px-4 py-2 rounded-xl text-xs font-semibold text-white text-center hover:opacity-90"
                  style="background-color: #4a90d9"
                  >Review</router-link
                >
              </div>
            </div>
          </div>
          <div
            v-if="!displayedSessions.length"
            class="text-center py-16 rounded-2xl border"
            style="background-color: #fff; border-color: #e8f0fe"
          >
            <p class="text-base font-semibold" style="color: #1b3a5c">
              No {{ activeTab }} sessions
            </p>
            <router-link
              v-if="activeTab === 'upcoming'"
              to="/tutors"
              class="inline-block mt-4 px-6 py-2.5 rounded-xl text-sm font-semibold text-white"
              style="background-color: #4a90d9"
              >Find Tutors</router-link
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
