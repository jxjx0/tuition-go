import { ref } from "vue"
import { tutorApi } from "../services/tutorApi"

interface TutorSubject {
    subject: string
    hourlyRate: number
    academicLevel: string
    tutorSubjectId: string
}

interface Tutor {
    tutorId: string
    name: string
    email: string
    phone: number
    bio: string
    imageURL: string
    averageRating: number
    totalReviews: number
    subjects: TutorSubject[]
}

export function useTutors() {

    const tutors = ref<Tutor[]>([])
    const loading = ref(false)
    const error = ref(null)

    async function searchTutors(filters:any = {}) {
        loading.value = true
        error.value = null

        try {

        const response = await tutorApi.get("/tutors/search", {
            params: {
            subject: filters.subject,
            academicLevel: filters.level,
            name: filters.name,
            sort: filters.sort
            }
        })

        tutors.value = response.data

        } catch (err:any) {
        error.value = err
        console.error(err)
        } finally {
        loading.value = false
        }
    }

    return {
        tutors,
        loading,
        error,
        searchTutors
    }
}

export function findTutorById() {

    const tutor = ref<Tutor | null>(null)
    const loading = ref(false)
    const error = ref(null)

    async function searchForTutor(tutorId: string) {
        loading.value = true
        error.value = null

        try {
            const response = await tutorApi.get(`/tutor/${tutorId}`)

            // store result reactively
            tutor.value = response.data

        } catch (err: any) {
            error.value = err
            console.error(err)
            return null
        } finally {
            loading.value = false
        }
    }

    return {
        tutor,
        loading,
        error,
        searchForTutor
    }
}