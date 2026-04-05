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
      return api.post('/complete-session/complete', { session_id: sessionId, tutor_id: tutorId })
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

    /**
     * Cancel a booked session.
     * Triggers the cancel-session composite service which handles:
     * session status update → Stripe refund → slot restoration → calendar update.
     */
    cancelSession(sessionId: string, studentId: string) {
      return api.post('/cancel-session/cancel', {
        session_id: sessionId,
        student_id: studentId,
      })
    },
  }
}

