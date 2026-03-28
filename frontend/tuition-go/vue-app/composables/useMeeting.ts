import { ref } from 'vue'
import { createGoogleMeeting, type MeetingRequest, type MeetingResponse } from '../services/meetingService'
import { useApi } from '../services/api'

/**
 * Layer 3: Meeting Composable
 * Manages reactive state for the meeting creation flow.
 */
export function useMeeting() {
    const loading = ref(false)
    const error = ref<string | null>(null)
    const result = ref<MeetingResponse | null>(null)
    const api = useApi()

    async function createMeeting(data: MeetingRequest) {
        loading.value = true
        error.value = null
        try {
            const res = await createGoogleMeeting(api, data)
            result.value = res
            return res
        } catch (err: any) {
            const errMsg = err.response?.data?.error || err.message || 'Failed to create meeting'
            error.value = errMsg
            throw err
        } finally {
            loading.value = false
        }
    }

    return {
        loading,
        error,
        result,
        createMeeting
    }
}
