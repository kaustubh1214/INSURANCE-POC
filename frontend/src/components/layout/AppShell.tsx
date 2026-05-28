import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'

interface NavItem {
  to: string
  label: string
  icon: string
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard',  label: 'Dashboard',      icon: '◼' },
  { to: '/policies',   label: 'My Policies',    icon: '📋' },
  { to: '/claims',     label: 'Claims',         icon: '🗂️' },
  { to: '/family',     label: 'Family Members', icon: '👨‍👩‍👧' },
  { to: '/health-card',label: 'Health Card',    icon: '💳' },
  { to: '/checkups',   label: 'Health Checkups',icon: '🏥' },
  { to: '/tickets',    label: 'Support',        icon: '🎫' },
]

const ADMIN_NAV: NavItem[] = [
  { to: '/admin', label: 'Admin Panel', icon: '⚙️' },
]

export default function AppShell() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleLogout = async () => {
    try { await authService.logout() } catch {}
    logout()
    navigate('/login')
  }

  const isAdmin = user?.role === 'admin' || user?.role === 'hr' || user?.role === 'insurer'

  const Sidebar = ({ mobile = false }: { mobile?: boolean }) => (
    <aside
      className={
        mobile
          ? 'fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 transform transition-transform duration-200 ' +
            (sidebarOpen ? 'translate-x-0' : '-translate-x-full')
          : 'hidden lg:flex flex-col w-64 bg-gray-900 min-h-screen fixed top-0 left-0'
      }
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-700">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white font-black text-xs">IB</span>
        </div>
        <div>
          <p className="text-white font-bold text-sm leading-none">InsureBridge</p>
          <p className="text-gray-400 text-xs mt-0.5 capitalize">{user?.role} Portal</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider px-3 mb-2">
          Main Menu
        </p>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ` +
              (isActive
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white')
            }
          >
            <span className="text-base w-5 text-center">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}

        {isAdmin && (
          <>
            <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider px-3 mt-5 mb-2">
              Administration
            </p>
            {ADMIN_NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ` +
                  (isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white')
                }
              >
                <span className="text-base w-5 text-center">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* User card */}
      <div className="px-4 py-4 border-t border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">
              {user?.full_name?.charAt(0)?.toUpperCase() ?? 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-xs font-semibold truncate">{user?.full_name}</p>
            <p className="text-gray-400 text-xs truncate capitalize">{user?.role}</p>
          </div>
          <button
            onClick={handleLogout}
            title="Logout"
            className="text-gray-500 hover:text-red-400 transition text-sm"
          >
            ⇥
          </button>
        </div>
      </div>
    </aside>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Desktop sidebar */}
      <Sidebar />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <Sidebar mobile />

      {/* Main content area */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 lg:px-8 h-14 flex items-center justify-between">
          {/* Mobile menu button */}
          <button
            className="lg:hidden text-gray-500 hover:text-gray-700 p-1"
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Breadcrumb placeholder */}
          <div className="hidden lg:block" />

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Notification bell (placeholder) */}
            <button className="relative text-gray-400 hover:text-gray-600 transition">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-9.33-4.994M9 17H4l1.405-1.405A2.032 2.032 0 006 14.158V11a6.002 6.002 0 009-5.197" />
              </svg>
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 hover:bg-gray-100 rounded-xl px-3 py-1.5 transition"
              >
                <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {user?.full_name?.charAt(0)?.toUpperCase() ?? 'U'}
                  </span>
                </div>
                <span className="hidden sm:block text-sm font-medium text-gray-700">
                  {user?.full_name?.split(' ')[0]}
                </span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-gray-100 z-20 py-1">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-semibold text-gray-800">{user?.full_name}</p>
                      <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full capitalize font-medium">
                        {user?.role}
                      </span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition flex items-center gap-2"
                    >
                      <span>→</span> Sign out
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
