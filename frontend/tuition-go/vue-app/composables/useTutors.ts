import { ref } from "vue"
import { useTutorService } from "../services/tutorService"

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
    const tutorService = useTutorService()

    async function searchTutors(filters:any = {}) {
        loading.value = true
        error.value = null

        try {

        const response = await tutorService.search({
            subject: filters.subject,
            academicLevel: filters.level,
            name: filters.name,
            sort: filters.sort
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
    const tutorService = useTutorService()

    async function searchForTutor(tutorId: string) {
        loading.value = true
        error.value = null

        try {
            const response = await tutorService.getById(tutorId)

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

    async function addSubject(
        tutorId: string,
        subject: string,
        academicLevel: string,
        hourlyRate: number,
    ) {
        try {
        const response = await tutorService.addSubject(tutorId, {
            subject,
            academicLevel,
            hourlyRate,
        });

        return response.data;
        } catch (err: any) {
        error.value = err;
        console.error(err);
        throw err;
        } finally {
        loading.value = false;
        }
    }

    async function updateProfile(tutorId: string, formData: FormData) {
        try {
            const response = await tutorService.updateProfile(tutorId, formData)
            return response.data
        } catch (err: any) {
            error.value = err
            console.error(err)
            throw err
        }
    }

    async function deleteSubject(
        tutorId: string,
        subjectId: string
    ) {
        try {
        const response = await tutorService.deleteSubject(tutorId, subjectId);

        return response.data;
        } catch (err: any) {
        error.value = err;
        console.error(err);
        throw err;
        } finally {
        loading.value = false;
        }
    }

    return {
        tutor,
        loading,
        error,
        searchForTutor,
        addSubject,
        deleteSubject
    }
}
