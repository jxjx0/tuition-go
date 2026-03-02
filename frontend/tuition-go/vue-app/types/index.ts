export interface Student {
  id: string
  clerkId: string
  name: string
  email: string
  avatar: string
  level: string
  joinedAt: string
}

export interface Tutor {
  id: string
  clerkId: string
  name: string
  email: string
  avatar: string
  bio: string
  qualifications: string[]
  subjects: Subject[]
  hourlyRate: number
  rating: number
  totalReviews: number
  totalSessions: number
  teachingStyle: string
  verified: boolean
  joinedAt: string
}

export interface Subject {
  name: string
  level: string
}

export interface Session {
  id: string
  tutorId: string
  tutorName: string
  tutorAvatar: string
  studentId: string
  studentName: string
  studentAvatar: string
  subject: string
  level: string
  date: string
  startTime: string
  endTime: string
  duration: number
  status: 'available' | 'booked' | 'completed' | 'cancelled'
  price: number
  meetingLink: string
  notes: string
}

export interface Review {
  id: string
  sessionId: string
  studentId: string
  studentName: string
  studentAvatar: string
  tutorId: string
  tutorName: string
  rating: number
  comment: string
  createdAt: string
  subject: string
}

export interface TimeSlot {
  id: string
  date: string
  startTime: string
  endTime: string
  available: boolean
}

export interface BookingConfirmation {
  sessionId: string
  tutorName: string
  subject: string
  date: string
  time: string
  price: number
  meetingLink: string
}

export type UserRole = 'student' | 'tutor'

export interface Notification {
  id: string
  type: 'booking' | 'cancellation' | 'review' | 'reminder'
  message: string
  read: boolean
  createdAt: string
}
