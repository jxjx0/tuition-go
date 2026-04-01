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

    updateSessionWithCalendar(sessionId: string, payload: {
      tutorSubjectId: string
      startTime: string
      endTime: string
      durationMins: number
      summary: string
      timezone: string
    }) {
      return api.put(`/update-session/${sessionId}`, payload)
    },

    deleteSession(sessionId: string) {
      return api.delete(`/delete-session/${sessionId}`)
    },

    completeSession(sessionId: string, tutorId: string) {
      return api.post(`/sessions/${sessionId}/complete`, { tutorId })
    },

    createSessionWithCalendar(payload: {
      tutorId: string
      tutorSubjectId: string
      startTime: string
      endTime: string
      durationMins: number
      summary: string
      timezone: string
    }) {
      return api.post('/create-session/create-session', payload)
    },
  }
}
