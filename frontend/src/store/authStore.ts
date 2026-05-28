/**
 * Zustand auth store — global authentication state.
 * Persists tokens to localStorage via tokenStorage utility.
 */
import { create } from 'zustand'
import type { CurrentUser } from '@/types'
import { tokenStorage } from '@/services/api'

interface AuthState {
  user: CurrentUser | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: CurrentUser) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!tokenStorage.getAccess(),
  isLoading: false,

  setUser: (user) => set({ user, isAuthenticated: true }),
  setLoading: (isLoading) => set({ isLoading }),
  logout: () => {
    tokenStorage.clear()
    set({ user: null, isAuthenticated: false })
  },
}))
