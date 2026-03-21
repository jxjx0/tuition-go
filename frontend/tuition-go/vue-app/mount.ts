import { createApp, defineComponent } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { clerkPlugin } from '@clerk/vue'
import { Navbar, Footer, StarRating } from './components'
import App from './App.vue'
import LandingPage from './pages/LandingPage.vue'
import LoginPage from './pages/LoginPage.vue'
import SignUpPage from './pages/SignUpPage.vue'
import StudentDashboardPage from './pages/StudentDashboardPage.vue'
import TutorDashboardPage from './pages/TutorDashboardPage.vue'
import BrowseTutorsPage from './pages/BrowseTutorsPage.vue'
import BrowseTutorsPage2 from './pages/BrowseTutorsPage2.vue'
import TutorDetailPage from './pages/TutorDetailPage.vue'
import TutorDetailPage2 from './pages/TutorDetailPage2.vue'
import BookSessionPage from './pages/BookSessionPage.vue'
import SessionDetailPage from './pages/SessionDetailPage.vue'
import ReviewPage from './pages/ReviewPage.vue'
import TutorSessionEditPage from './pages/TutorSessionEditPage.vue'
import TutorEditProfilePage from './pages/TutorEditProfilePage.vue'
import TutorEditProfilePage2 from './pages/TutorEditProfilePage2.vue'
import AuthRedirectPage from './pages/AuthRedirectPage.vue'
import StudentEditProfilePage from './pages/StudentEditProfilePage.vue'

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/signup', name: 'signup', component: SignUpPage },
  { path: '/tutors', name: 'tutors2', component: BrowseTutorsPage2 },
  { path: '/tutors2', name: 'tutors', component: BrowseTutorsPage },
  { path: '/tutors/:id', name: 'tutor-detail2', component: TutorDetailPage2, props: true },
  { path: '/tutors2/:id', name: 'tutor-detail', component: TutorDetailPage, props: true },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: StudentDashboardPage,
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/tutor-dashboard',
    name: 'tutor-dashboard',
    component: TutorDashboardPage,
    meta: { requiresAuth: true, role: 'tutor' },
  },
  { path: '/book/:sessionId', name: 'book-session', component: BookSessionPage, props: true },
  { path: '/session/:id', name: 'session-detail', component: SessionDetailPage, props: true, meta: { requiresAuth: true } },
  { path: '/review/:sessionId', name: 'review', component: ReviewPage, props: true },
  { path: '/tutor-profile/:id', name: 'TutorProfile2', component: TutorEditProfilePage2 },
  { path: '/tutor-session/:sessionId', name: 'TutorSessionEdit', component: TutorSessionEditPage, meta: { requiresAuth: true, role: 'tutor' } },
  { path: '/tutor-profile2/', name: 'TutorProfile', component: TutorEditProfilePage },
  {
    path: '/student-profile',
    name: 'student-profile',
    component: StudentEditProfilePage,
    meta: { requiresAuth: true, role: 'student' },
  },
  { path: '/auth-redirect', name: 'auth-redirect', component: AuthRedirectPage },
  { path: '/debug-meeting', name: 'debug-meeting', component: () => import('./pages/TestMeetingPage.vue') },

]

export function mountVueApp(el: HTMLElement) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() { return { top: 0 } },
  })

  router.beforeEach(async (to) => {
    const requiresAuth = Boolean(to.meta.requiresAuth)
    const requiredRole = typeof to.meta.role === 'string' ? to.meta.role : null

    if (!requiresAuth) {
      return true
    }

    const clerk = (window as any).Clerk

    if (!clerk) {
      return {
        path: '/login',
        query: { redirect: to.fullPath },
      }
    }

    if (!clerk.loaded) {
      await clerk.load()
    }

    if (!clerk.user) {
      return {
        path: '/login',
        query: { redirect: to.fullPath },
      }
    }

    const userRole = clerk.user.unsafeMetadata?.role
    if (requiredRole && userRole !== requiredRole) {
      return userRole === 'tutor' ? '/tutor-dashboard' : '/dashboard'
    }

    return true
  })

  const app = createApp(App)
  app.use(clerkPlugin, {
    publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY as string,
  })
  app.use(router)
  app.mount(el)
  return app
}
