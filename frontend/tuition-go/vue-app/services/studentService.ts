import { useApi } from './api'

/**
 * Student service — pure functions that map to student API endpoints.
 * Register and lookup endpoints require authentication.
 */
export function useStudentService() {
  const api = useApi()

  return {
    register(payload: { name: string; email: string; clerkUserId: string; phone?: string }) {
      return api.post('/students/register', payload)
    },

    getById(studentId: string) {
      return api.get(`/students/${studentId}`)
    },

    getByClerkId(clerkUserId: string) {
      return api.get(`/students/by-clerk/${clerkUserId}`)
    },

    update(studentId: string, formData: FormData) {
      return api.put(`/students/${studentId}`, formData, {
        headers: { 'Content-Type': undefined },
      })
    },

    remove(studentId: string) {
      return api.delete(`/students/${studentId}`)
    },
  }
}
