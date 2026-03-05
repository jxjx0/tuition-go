import { ref } from "vue"
import { tutorApi } from "../services/tutorApi"

export function useTutors() {

    const tutors = ref([])
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