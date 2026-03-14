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
  }
}
