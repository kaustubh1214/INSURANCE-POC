import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'
import { tokenStorage } from '@/services/api'

// Layout
import AppShell from '@/components/layout/AppShell'

// Auth
import LoginPage from '@/pages/auth/LoginPage'

// Pages
import DashboardPage      from '@/pages/dashboard/DashboardPage'
import PoliciesPage       from '@/pages/policies/PoliciesPage'
import ClaimsPage         from '@/pages/claims/ClaimsPage'
import FamilyPage         from '@/pages/family/FamilyPage'
import HealthCardPage     from '@/pages/health/HealthCardPage'
import HealthCheckupsPage from '@/pages/health/HealthCheckupsPage'
import TicketsPage        from '@/pages/tickets/TicketsPage'
import AdminPage          from '@/pages/admin/AdminPage'

// ── Protected route wrapper ──────────────────────────────────────────────────
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

// ── Role-based route guard ───────────────────────────────────────────────────
function RoleRoute({
  children,
  roles,
}: {
  children: React.ReactNode
  roles: string[]
}) {
  const user = useAuthStore(s => s.user)
  if (user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }
  return <>{children}</>
}

// ── Loading screen ───────────────────────────────────────────────────────────
function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-12 h-12 bg-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span className="text-white font-black text-lg">IB</span>
        </div>
        <div className="flex items-center gap-2 text-gray-400 text-sm">
          <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Loading InsureBridge…
        </div>
      </div>
    </div>
  )
}

// ── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const { setUser, setLoading, isLoading, logout } = useAuthStore()

  // Restore session on page load / refresh
  useEffect(() => {
    const token = tokenStorage.getAccess()
    if (token) {
      setLoading(true)
      authService
        .getMe()
        .then(setUser)
        .catch(() => logout())
        .finally(() => setLoading(false))
    }
  }, [])

  if (isLoading) return <LoadingScreen />

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected — wrapped in AppShell sidebar layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          {/* Default redirect */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          {/* Employee pages */}
          <Route path="dashboard"   element={<DashboardPage />} />
          <Route path="policies"    element={<PoliciesPage />} />
          <Route path="claims"      element={<ClaimsPage />} />
          <Route path="family"      element={<FamilyPage />} />
          <Route path="health-card" element={<HealthCardPage />} />
          <Route path="checkups"    element={<HealthCheckupsPage />} />
          <Route path="tickets"     element={<TicketsPage />} />

          {/* Admin / HR / Insurer only */}
          <Route
            path="admin"
            element={
              <RoleRoute roles={['admin', 'hr', 'insurer']}>
                <AdminPage />
              </RoleRoute>
            }
          />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
