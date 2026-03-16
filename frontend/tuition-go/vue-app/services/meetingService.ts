import { useApi, publicApi } from './api'

export interface MeetingRequest {
    summary: string
    description?: string
    start_time: string
    end_time: string
    timezone?: string
    attendees?: string[]
}

export interface MeetingResponse {
    message: string
    htmlLink: string
    hangoutLink: string
    eventId: string
}

/**
 * Layer 2: Meeting Service
 * Pure functions for interacting with the meeting/calendar endpoints.
 */
export async function createGoogleMeeting(data: MeetingRequest, googleToken?: string, userEmail?: string): Promise<MeetingResponse> {
    const api = publicApi
    const headers: Record<string, string> = {}
    if (googleToken) {
        headers['X-Google-Token'] = googleToken
    }
    if (userEmail) {
        headers['X-User-Email'] = userEmail
    }
    const response = await api.post<MeetingResponse>('/calendar/create-meeting', data, { headers })
    return response.data
}
