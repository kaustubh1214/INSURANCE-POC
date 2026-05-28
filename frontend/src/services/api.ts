/**
 * Axios API client — centralized HTTP layer.
 * - Attaches JWT Bearer token to every request
 * - Handles 401 → auto-refresh or redirect to login
 * - Parses standard APIResponse envelope
 */
import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import type { APIResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

// ---------------------------------------------------------------------------
// Token Management (localStorage)
// ---------------------------------------------------------------------------
const TOKEN_KEY = 'insurebridge_access_token'
const REFRESH_KEY = 'insurebridge_refresh_token'

export const tokenStorage = {
  getAccess: (): string | null => localStorage.getItem(TOKEN_KEY),
  getRefresh: (): string | null => localStorage.getItem(REFRESH_KEY),
  setTokens: (access: string, refresh: string): void => {
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: (): void => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

// ---------------------------------------------------------------------------
// Axios Instance
// ---------------------------------------------------------------------------
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}${API_PREFIX}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: inject Bearer token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccess()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 with token refresh
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue requests while refresh is in progress
        return new Promise((resolve) => {
          refreshSubscribers.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = tokenStorage.getRefresh()
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${BASE_URL}${API_PREFIX}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = data.data
        tokenStorage.setTokens(access_token, refresh_token)

        refreshSubscribers.forEach((cb) => cb(access_token))
        refreshSubscribers = []

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch {
        tokenStorage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// ---------------------------------------------------------------------------
// Typed API call helpers
// ---------------------------------------------------------------------------
export async function apiGet<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<APIResponse<T>> {
  const response = await apiClient.get<APIResponse<T>>(url, config)
  return response.data
}

export async function apiPost<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<APIResponse<T>> {
  const response = await apiClient.post<APIResponse<T>>(url, data, config)
  return response.data
}

export async function apiPut<T>(
  url: string,
  data?: unknown
): Promise<APIResponse<T>> {
  const response = await apiClient.put<APIResponse<T>>(url, data)
  return response.data
}

export async function apiDelete<T>(url: string): Promise<APIResponse<T>> {
  const response = await apiClient.delete<APIResponse<T>>(url)
  return response.data
}
