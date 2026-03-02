// @ts-ignore
import { defineComponent, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { StarRating } from '../components'
import { getTutorById, getAvailableSessionsByTutorId, getReviewsByTutorId } from '../composables/useMockData'

function formatDate(d: string) { return new Date(d).toLocaleDateString('en-SG', { weekday:'short', day:'numeric', month:'short', year:'numeric' }) }

export const TutorDetailPage = defineComponent({
  name: 'TutorDetailPage',
  components: { RouterLink, StarRating },
  setup() {
    const route = useRoute()
    const tutorId = computed(() => route.params.id as string)
    const tutor = computed(() => getTutorById(tutorId.value))
    const availableSessions = computed(() => getAvailableSessionsByTutorId(tutorId.value))
    const tutorReviews = computed(() => getReviewsByTutorId(tutorId.value))
    return { tutor, availableSessions, tutorReviews, formatDate }
  },
  template: `
    <div class="py-8 md:py-12" style="background-color:#F5F7FA">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8" v-if="tutor">
        <router-link to="/tutors" class="inline-flex items-center gap-2 text-sm font-medium mb-6 hover:opacity-80" style="color:#4A90D9"><svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>Back to Tutors</router-link>
        <div class="rounded-2xl border overflow-hidden mb-8" style="background-color:#fff;border-color:#E8F0FE">
          <div class="p-6 md:p-8" style="background:linear-gradient(135deg,#1B3A5C 0%,#4A90D9 100%)">
            <div class="flex flex-col md:flex-row items-start gap-6">
              <div class="relative flex-shrink-0"><img :src="tutor.avatar" :alt="tutor.name" class="w-24 h-24 md:w-28 md:h-28 rounded-2xl object-cover border-4 border-white shadow-lg" crossorigin="anonymous" style="background-color:#E8F0FE"/><div v-if="tutor.verified" class="absolute -bottom-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center shadow-sm" style="background-color:#2EAA4F"><svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg></div></div>
              <div class="flex-1"><h1 class="text-2xl md:text-3xl font-extrabold text-white">{{ tutor.name }}</h1><div class="flex flex-wrap items-center gap-4 mt-3"><div class="flex items-center gap-1"><StarRating :modelValue="tutor.rating" size="sm"/><span class="text-sm font-bold text-white ml-1">{{ tutor.rating }}</span><span class="text-sm" style="color:rgba(255,255,255,0.7)">({{ tutor.totalReviews }} reviews)</span></div><span class="text-sm" style="color:rgba(255,255,255,0.7)">{{ tutor.totalSessions }} sessions</span></div><div class="flex flex-wrap gap-2 mt-4"><span v-for="sub in tutor.subjects" :key="sub.name+sub.level" class="px-3 py-1 rounded-lg text-xs font-medium" style="background-color:rgba(255,255,255,0.2);color:#fff">{{ sub.name }} ({{ sub.level }})</span></div></div>
              <div class="flex-shrink-0 text-center md:text-right"><p class="text-3xl font-extrabold text-white">\${{ tutor.hourlyRate }}</p><p class="text-sm" style="color:rgba(255,255,255,0.7)">per hour</p></div>
            </div>
          </div>
          <div class="p-6 md:p-8">
            <div class="mb-8"><h2 class="text-lg font-bold mb-3" style="color:#1B3A5C">About</h2><p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.8">{{ tutor.bio }}</p></div>
            <div class="mb-8"><h2 class="text-lg font-bold mb-3" style="color:#1B3A5C">Qualifications</h2><div class="flex flex-wrap gap-2"><span v-for="q in tutor.qualifications" :key="q" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium" style="background-color:#E8F0FE;color:#4A90D9"><svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>{{ q }}</span></div></div>
            <div class="mb-8"><h2 class="text-lg font-bold mb-3" style="color:#1B3A5C">Teaching Style</h2><p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.8">{{ tutor.teachingStyle }}</p></div>
          </div>
        </div>
        <div class="rounded-2xl border p-6 md:p-8 mb-8" style="background-color:#fff;border-color:#E8F0FE">
          <h2 class="text-lg font-bold mb-6" style="color:#1B3A5C">Available Sessions</h2>
          <div v-if="availableSessions.length" class="space-y-3">
            <div v-for="session in availableSessions" :key="session.id" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl border hover:shadow-sm" style="border-color:#E8F0FE">
              <div class="flex items-center gap-4"><div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background-color:#E8F0FE"><svg class="w-6 h-6" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg></div><div><p class="text-sm font-semibold" style="color:#1B3A5C">{{ session.subject }} ({{ session.level }})</p><p class="text-xs mt-0.5" style="color:#1B3A5C;opacity:0.6">{{ formatDate(session.date) }} &middot; {{ session.startTime }} - {{ session.endTime }}</p></div></div>
              <div class="flex items-center gap-4"><p class="text-lg font-bold" style="color:#2EAA4F">\${{ session.price.toFixed(2) }}</p><router-link :to="'/book/'+session.id" class="px-5 py-2.5 rounded-xl text-sm font-semibold text-white hover:opacity-90" style="background-color:#2EAA4F">Book Now</router-link></div>
            </div>
          </div>
          <div v-else class="text-center py-12"><div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-3" style="background-color:#E8F0FE"><svg class="w-7 h-7" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg></div><p class="text-sm font-medium" style="color:#1B3A5C">No available sessions at the moment</p></div>
        </div>
        <div class="rounded-2xl border p-6 md:p-8" style="background-color:#fff;border-color:#E8F0FE">
          <div class="flex items-center justify-between mb-6"><h2 class="text-lg font-bold" style="color:#1B3A5C">Student Reviews</h2><span class="text-sm font-medium px-3 py-1 rounded-lg" style="background-color:#E8F0FE;color:#4A90D9">{{ tutorReviews.length }} reviews</span></div>
          <div v-if="tutorReviews.length" class="space-y-4">
            <div v-for="review in tutorReviews" :key="review.id" class="p-4 rounded-xl border" style="border-color:#E8F0FE">
              <div class="flex items-center gap-3 mb-3"><img :src="review.studentAvatar" :alt="review.studentName" class="w-10 h-10 rounded-full" crossorigin="anonymous" style="background-color:#E8F0FE"/><div class="flex-1 min-w-0"><p class="text-sm font-semibold" style="color:#1B3A5C">{{ review.studentName }}</p><div class="flex items-center gap-2"><StarRating :modelValue="review.rating" size="sm"/><span class="text-xs" style="color:#1B3A5C;opacity:0.5">{{ review.subject }} &middot; {{ formatDate(review.createdAt) }}</span></div></div></div>
              <p class="text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.8">{{ review.comment }}</p>
            </div>
          </div>
          <div v-else class="text-center py-8"><p class="text-sm" style="color:#1B3A5C;opacity:0.6">No reviews yet</p></div>
        </div>
      </div>
      <div v-else class="text-center py-20"><h2 class="text-2xl font-bold" style="color:#1B3A5C">Tutor not found</h2><router-link to="/tutors" class="mt-4 inline-block px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Browse Tutors</router-link></div>
    </div>
  `,
})
