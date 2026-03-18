import { useApi } from './api'

/**
 * Tutor service — all endpoints go through authenticated api (Kong ACL requires it).
 */
export function useTutorService() {
  const api = useApi()

  return {
    search(params: { subject?: string; academicLevel?: string; name?: string; sort?: string }) {
      return api.get('/tutors/tutors/search', { params })
    },

    register(payload: { name: string; email: string; clerkUserId: string; phone?: string; password?: string }) {
      return api.post('/tutors/tutor/register', payload)
    },

    getById(tutorId: string) {
      return api.get(`/tutors/tutor/${tutorId}`)
    },

    getSubjects(tutorId: string) {
      return api.get(`/tutors/tutor/${tutorId}/subjects`)
    },

    // Protected endpoints (auth required)
    updateProfile(tutorId: string, formData: FormData) {
      return api.put(`/tutors/tutor/${tutorId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },

    addSubject(tutorId: string, data: { subject: string; academicLevel: string; hourlyRate: number }) {
      return api.post(`/tutors/tutor/${tutorId}/subjects`, data)
    },

    deleteSubject(tutorId: string, subjectId: string) {
      return api.delete(`/tutors/tutor/${tutorId}/subjects/${subjectId}`)
    },
  }
}
