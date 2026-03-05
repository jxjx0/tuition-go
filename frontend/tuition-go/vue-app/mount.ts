// @ts-ignore - need runtime compiler for template strings
import * as Vue from 'vue'
import { createRouter, createWebHashHistory, RouterView, RouterLink } from 'vue-router'
import { Navbar, Footer, StarRating } from './components'
import { LandingPage } from './pages/landing'
import { LoginPage } from './pages/login'
import { SignUpPage } from './pages/signup'
import { BrowseTutorsPage } from './pages/browse-tutors'
import { TutorDetailPage } from './pages/tutor-detail'
import { StudentDashboardPage } from './pages/student-dashboard'
import { TutorDashboardPage } from './pages/tutor-dashboard'
import { BookSessionPage } from './pages/book-session'
import { SessionDetailPage } from './pages/session-detail'
import { ReviewPage } from './pages/review'
import {TutorEditProfilePage} from './pages/tutor-profile-edit'
import { BrowseTutorsPage2 } from './pages/browse-tutors-2'

const { createApp, defineComponent } = Vue

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/signup', name: 'signup', component: SignUpPage },
  { path: '/tutors', name: 'tutors2', component: BrowseTutorsPage2 },
  { path: '/tutors2', name: 'tutors', component: BrowseTutorsPage },
  { path: '/tutors/:id', name: 'tutor-detail', component: TutorDetailPage, props: true },
  { path: '/dashboard', name: 'dashboard', component: StudentDashboardPage },
  { path: '/tutor-dashboard', name: 'tutor-dashboard', component: TutorDashboardPage },
  { path: '/book/:sessionId', name: 'book-session', component: BookSessionPage, props: true },
  { path: '/session/:id', name: 'session-detail', component: SessionDetailPage, props: true },
  { path: '/review/:sessionId', name: 'review', component: ReviewPage, props: true },
  { path: '/tutor-profile/', name: 'TutorProfile', component: TutorEditProfilePage },
]

const App = defineComponent({
  name: 'App',
  components: { Navbar, Footer, RouterView },
  template: `
    <div class="min-h-screen flex flex-col" style="background-color:#F5F7FA;color:#1B3A5C;font-family:'Geist','Geist Fallback',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
      <Navbar />
      <main class="flex-1">
        <router-view />
      </main>
      <Footer />
    </div>
  `,
})

export function mountVueApp(el: HTMLElement) {
  const router = createRouter({
    history: createWebHashHistory(),
    routes,
    scrollBehavior() { return { top: 0 } },
  })

  const app = createApp(App)
  app.use(router)
  app.mount(el)
  return app
}
