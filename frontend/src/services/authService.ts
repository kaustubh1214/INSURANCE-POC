/**
 * Auth API service — login, register, logout, token refresh.
 */
import { apiPost, apiGet, tokenStorage } from './api'
import type { TokenResponse, CurrentUser } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<CurrentUser> {
    const response = await apiPost<TokenResponse>('/auth/login', { email, password })
    if (!response.success || !response.data) throw new Error(response.message)

    tokenStorage.setTokens(response.data.access_token, response.data.refresh_token)

    const meResponse = await apiGet<CurrentUser>('/auth/me')
    if (!meResponse.success || !meResponse.data) throw new Error('Failed to get user')
    return meResponse.data
  },

  async register(payload: {
    email: string
    password: string
    full_name: string
    phone?: string
    role?: string
  }): Promise<CurrentUser> {
    const response = await apiPost<CurrentUser>('/auth/register', payload)
    if (!response.success || !response.data) throw new Error(response.message)
    return response.data
  },

  async logout(): Promise<void> {
    try {
      await apiPost('/auth/logout')
    } finally {
      tokenStorage.clear()
    }
  },

  async getMe(): Promise<CurrentUser> {
    const response = await apiGet<CurrentUser>('/auth/me')
    if (!response.success || !response.data) throw new Error(response.message)
    return response.data
  },
}
