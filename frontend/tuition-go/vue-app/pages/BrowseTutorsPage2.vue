<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { StarRating } from '../components'
import { useTutors } from "../composables/useTutors"

const { tutors, searchTutors, loading } = useTutors()

const searchQuery = ref('')
const subjectFilter = ref('')
const levelFilter = ref('')
const sortBy = ref('')

const allSubjects = [
  "Mathematics",
  "Additional Mathematics",
  "English",
  "Science",
  "Chinese",
  "Malay",
  "Tamil",
  "Physics",
  "Chemistry",
  "Biology",
  "Economics",
  "Geography",
  "History",
  "Literature",
  "General Paper",
  "Computer Science"
]

const allLevels = [
  "Primary 1",
  "Primary 2",
  "Primary 3",
  "Primary 4",
  "Primary 5",
  "Primary 6",
  "Secondary 1",
  "Secondary 2",
  "Secondary 3",
  "Secondary 4",
  "JC",
  "IB"
]

onMounted(() => {
  searchTutors({
    name: searchQuery.value,
    subject: subjectFilter.value,
    academicLevel: levelFilter.value,
    sort: sortBy.value,
  });
});

const filteredTutors = computed(() => tutors.value)

function clearFilters() { 
  searchQuery.value = ''
  subjectFilter.value = ''
  levelFilter.value = '' 
}

watch([searchQuery, subjectFilter, levelFilter, sortBy], () => {
  searchTutors({
    name: searchQuery.value,
    subject: subjectFilter.value,
    academicLevel: levelFilter.value,
    sort: sortBy.value
  })
})
</script>

<template>
  <div class="py-8 md:py-12" style="background-color:#F5F7FA">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="mb-10">
        <h1 class="text-3xl md:text-4xl font-extrabold" style="color:#1B3A5C">Find Your Tutor</h1>
        <p class="mt-2 text-base" style="color:#1B3A5C;opacity:0.65">{{ filteredTutors.length }} qualified tutors available</p>
      </div>
      <div class="rounded-2xl p-4 md:p-6 mb-8 border" style="background-color:#fff;border-color:#E8F0FE">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1 relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input v-model="searchQuery" type="text" placeholder="Search by name ..." class="w-full pl-10 pr-4 py-3 rounded-xl text-sm border" style="border-color:#E8F0FE;color:#1B3A5C"/>
          </div>
          <select v-model="subjectFilter" class="px-4 py-3 rounded-xl text-sm border cursor-pointer" style="border-color:#E8F0FE;color:#1B3A5C;min-width:160px">
            <option value="">All Subjects</option>
            <option v-for="s in allSubjects" :key="s" :value="s">{{ s }}</option>
          </select>
          <select v-model="levelFilter" class="px-4 py-3 rounded-xl text-sm border cursor-pointer" style="border-color:#E8F0FE;color:#1B3A5C;min-width:140px">
            <option value="">All Levels</option>
            <option v-for="l in allLevels" :key="l" :value="l">{{ l }}</option>
          </select>
          <select v-model="sortBy" class="px-4 py-3 rounded-xl text-sm border cursor-pointer" style="border-color:#E8F0FE;color:#1B3A5C;min-width:160px">
            <option value="">No Sorting</option>
            <option value="highestRated">Highest Rated</option>
            <option value="mostReviews">Most Reviews</option>
          </select>
        </div>
        <div v-if="subjectFilter||levelFilter||searchQuery" class="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t" style="border-color:#E8F0FE">
          <span class="text-xs font-medium" style="color:#1B3A5C;opacity:0.6">Active filters:</span>
          <button v-if="searchQuery" @click="searchQuery=''" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium" style="background-color:#E8F0FE;color:#4A90D9">
            "{{ searchQuery }}" 
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
          </button>
          <button v-if="subjectFilter" @click="subjectFilter=''" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium" style="background-color:#E8F0FE;color:#4A90D9">
            {{ subjectFilter }} 
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
          </button>
          <button v-if="levelFilter" @click="levelFilter=''" class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium" style="background-color:#E8F0FE;color:#4A90D9">
            {{ levelFilter }} 
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
      <div v-if="filteredTutors.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link v-for="tutor in filteredTutors" :key="tutor.tutorId" :to="'/tutors/'+tutor.tutorId" class="group rounded-2xl border bg-white overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-lg flex flex-col h-full">
          <div class="p-6 flex-1">
            <div class="flex items-start gap-4">
              <div class="relative flex-shrink-0">
                <img :src="tutor.imageURL" :alt="tutor.name" class="w-16 h-16 rounded-xl object-cover" crossorigin="anonymous" style="background-color:#E8F0FE"/>
                <div v-if="tutor.verified" class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center" style="background-color:#2EAA4F">
                  <svg class="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-bold truncate" style="color:#1B3A5C">{{ tutor.name }}</h3>
                <div class="flex items-center gap-2 mt-1">
                  <StarRating :modelValue="tutor.averageRating" size="sm"/>
                  <span class="text-sm font-semibold" style="color:#1B3A5C">{{ tutor.rating }}</span>
                  <span class="text-xs" style="color:#1B3A5C;opacity:0.5">({{ tutor.totalReviews }})</span>
                </div>
              </div>
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
              <span v-for="sub in tutor.subjects.slice(0,3)" :key="sub.subject+sub.academicLevel" class="px-2.5 py-1 rounded-lg text-xs font-medium" style="background-color:#E8F0FE;color:#4A90D9">{{ sub.subject }} ({{ sub.academicLevel }})</span>
              <span v-if="tutor.subjects.length>3" class="px-2.5 py-1 rounded-lg text-xs font-medium" style="background-color:#F5F7FA;color:#1B3A5C;opacity:0.6">+{{ tutor.subjects.length-3 }} more</span>
            </div>
            <p class="mt-3 text-sm leading-relaxed" style="color:#1B3A5C;opacity:0.7;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{{ tutor.bio }}</p>
          </div>
          <div class="px-6 py-4 flex items-center justify-between border-t" style="border-color:#E8F0FE;background-color:#F5F7FA">
            <span></span>
            <span class="text-xs font-semibold" style="color:#4A90D9">View Profile</span>
          </div>
        </router-link>
      </div>
      <div v-else class="text-center py-20">
        <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style="background-color:#E8F0FE">
          <svg class="w-8 h-8" style="color:#4A90D9" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-bold" style="color:#1B3A5C">No tutors found</h3>
        <p class="text-sm mt-2" style="color:#1B3A5C;opacity:0.6">Try adjusting your search filters</p>
        <button @click="clearFilters" class="mt-4 px-6 py-2 rounded-lg text-sm font-semibold text-white" style="background-color:#4A90D9">Clear All Filters</button>
      </div>
    </div>
  </div>
</template>
