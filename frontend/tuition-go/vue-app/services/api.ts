import axios from 'axios'
import { useAuth } from '@clerk/vue'

const KONG_BASE_URL = 'http://localhost:8000/api/v1'

/**
 * One shared authenticated Axios instance.
 * Created once, reused everywhere.
 */
const authApi = axios.create({
  baseURL: KONG_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let interceptorAttached = false

/**
 * Call once in a Vue component/composable to attach the Clerk token interceptor.
 * Safe to call multiple times — only attaches once.
 */
export function useApi() {
  if (!interceptorAttached) {
    const { getToken } = useAuth()

    authApi.interceptors.request.use(async (config) => {
      const token = await getToken.value()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    interceptorAttached = true
  }

  return authApi
}

/**
 * Public Axios instance (no auth token).
 * Use for endpoints that don't require authentication (e.g. browsing tutors).
 */
export const publicApi = axios.create({
  baseURL: KONG_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})
