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
import TutorEditProfilePage from './pages/TutorEditProfilePage.vue'
import TutorEditProfilePage2 from './pages/TutorEditProfilePage2.vue'
import SSOCallbackPage from './pages/SSOCallbackPage.vue'

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/signup', name: 'signup', component: SignUpPage },
  { path: '/tutors', name: 'tutors2', component: BrowseTutorsPage2 },
  { path: '/tutors2', name: 'tutors', component: BrowseTutorsPage },
  { path: '/tutors/:id', name: 'tutor-detail2', component: TutorDetailPage2, props: true },
  { path: '/tutors2/:id', name: 'tutor-detail', component: TutorDetailPage, props: true },
  { path: '/dashboard', name: 'dashboard', component: StudentDashboardPage },
  { path: '/tutor-dashboard', name: 'tutor-dashboard', component: TutorDashboardPage },
  { path: '/book/:sessionId', name: 'book-session', component: BookSessionPage, props: true },
  { path: '/session/:id', name: 'session-detail', component: SessionDetailPage, props: true },
  { path: '/review/:sessionId', name: 'review', component: ReviewPage, props: true },
  { path: '/tutor-profile/:id', name: 'TutorProfile2', component: TutorEditProfilePage2 },
  { path: '/tutor-profile2/', name: 'TutorProfile', component: TutorEditProfilePage },
  { path: '/sso-callback', name: 'sso-callback', component: SSOCallbackPage },

]

export function mountVueApp(el: HTMLElement) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() { return { top: 0 } },
  })

  const app = createApp(App)
  app.use(clerkPlugin, {
    publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY as string,
  })
  app.use(router)
  app.mount(el)
  return app
}
