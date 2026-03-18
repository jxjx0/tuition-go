import { ref } from 'vue'
import { createGoogleMeeting, type MeetingRequest, type MeetingResponse } from '../services/meetingService'
import { useUser, useAuth } from '@clerk/vue'

/**
 * Layer 3: Meeting Composable
 * Manages reactive state for the meeting creation flow.
 */
export function useMeeting() {
    const loading = ref(false)
    const error = ref<string | null>(null)
    const result = ref<MeetingResponse | null>(null)
    const { user } = useUser()

    async function createMeeting(data: MeetingRequest) {
        loading.value = true
        error.value = null
        try {
            // Get user email from Clerk session
            const userEmail = user.value?.primaryEmailAddress?.emailAddress
            if (!userEmail) {
                console.warn('Meeting: No primary email found in Clerk session.')
            }

            // We pass undefined for googleToken as it's not reliably available on frontend
            const res = await createGoogleMeeting(data, undefined, userEmail)
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
