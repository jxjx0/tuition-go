import { useApi } from './api'

/**
 * Student service — pure functions that map to student API endpoints.
 * Register and lookup endpoints require authentication.
 */
export function useStudentService() {
  const api = useApi()

  return {
    register(payload: { name: string; email: string; clerkUserId: string; phone?: string }) {
      return api.post('/students/student/register', payload)
    },

    getById(studentId: string) {
      return api.get(`/students/student/${studentId}`)
    },

    getByClerkId(clerkUserId: string) {
      return api.get(`/students/student/by-clerk/${clerkUserId}`)
    },

    update(studentId: string, payload: { name?: string; phone?: string; imageURL?: string }) {
      return api.put(`/students/student/${studentId}`, payload)
    },

    remove(studentId: string) {
      return api.delete(`/students/student/${studentId}`)
    },
  }
}
