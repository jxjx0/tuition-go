import type { AxiosInstance } from 'axios'

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
 * Pure functions for interacting with the calendar endpoint.
 */
export async function createGoogleMeeting(api: AxiosInstance, data: MeetingRequest): Promise<MeetingResponse> {
    const response = await api.post<MeetingResponse>('/calendar/create-meeting', data)
    return response.data
}
