import { useApi } from './api'

/**
 * Session service — pure functions that map to session API endpoints.
 * All session endpoints require authentication.
 */
export function useSessionService() {
  const api = useApi()

  return {
    getStudentSessions(studentId: string) {
      return api.get(`/getsessions/student/${studentId}/sessions`)
    },

    getTutorSessions(tutorId: string) {
      return api.get(`/getsessions/tutor/${tutorId}/sessions`)
    },

    getSessionById(sessionId: string) {
      return api.get(`/getsessions/session/${sessionId}`)
    },

    updateSession(sessionId: string, payload: {
      tutorSubjectId?: string
      startTime?: string
      endTime?: string
      durationMins?: number
      meetingLink?: string
    }) {
      return api.put(`/sessions/${sessionId}`, payload)
    },

    deleteSession(sessionId: string) {
      return api.delete(`/sessions/${sessionId}`)
    },

    createSession(payload: {
      tutorId: string
      tutorSubjectId: string
      startTime: string
      endTime: string
      status?: string
      durationMins?: number
    }) {
      return api.post('/sessions', payload)
    },
  }
}
