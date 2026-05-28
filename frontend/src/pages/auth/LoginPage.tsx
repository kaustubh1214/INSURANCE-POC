import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setUser } = useAuthStore()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!email || !password) {
      setError('Please enter your email and password.')
      return
    }
    setLoading(true)
    try {
      const user = await authService.login(email, password)
      setUser(user)
      navigate('/dashboard')
    } catch (err: any) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        'Login failed. Please check your credentials.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-700 to-blue-900 flex-col justify-between p-12 text-white">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
              <span className="text-blue-700 font-black text-lg">IB</span>
            </div>
            <span className="text-2xl font-bold tracking-tight">InsureBridge</span>
          </div>
          <h1 className="text-4xl font-bold leading-snug mb-4">
            Enterprise Insurance &amp;<br />Benefits Platform
          </h1>
          <p className="text-blue-200 text-lg leading-relaxed">
            Manage policies, claims, health cards, and employee benefits — powered by AI.
          </p>
        </div>

        {/* Feature pills */}
        <div className="space-y-3">
          {[
            '🛡️  Multi-policy management',
            '📋  AI-powered claim processing',
            '🏥  Health checkup scheduling',
            '👨‍👩‍👧  Family member coverage',
            '🔒  Enterprise-grade security',
          ].map((f) => (
            <div
              key={f}
              className="flex items-center gap-3 bg-white/10 rounded-xl px-4 py-2 text-sm text-blue-100"
            >
              {f}
            </div>
          ))}
        </div>
      </div>

      {/* Right login form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-9 h-9 bg-blue-700 rounded-xl flex items-center justify-center">
              <span className="text-white font-black">IB</span>
            </div>
            <span className="text-xl font-bold text-gray-900">InsureBridge</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Welcome back</h2>
          <p className="text-gray-500 mb-8">Sign in to your account to continue.</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Error banner */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-start gap-2">
                <span className="mt-0.5">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900
                           placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500
                           focus:border-transparent transition"
                autoComplete="email"
                disabled={loading}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900
                             placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500
                             focus:border-transparent transition pr-12"
                  autoComplete="current-password"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-sm"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-6 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-400
                         text-white font-semibold rounded-xl transition focus:outline-none
                         focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-xl text-sm text-blue-700">
            <p className="font-semibold mb-1">Demo credentials</p>
            <p>Email: <span className="font-mono">admin@insurebridge.com</span></p>
            <p>Password: <span className="font-mono">Admin@123456</span></p>
          </div>

          <p className="mt-6 text-center text-sm text-gray-400">
            InsureBridge © {new Date().getFullYear()} · Enterprise Edition
          </p>
        </div>
      </div>
    </div>
  )
}
