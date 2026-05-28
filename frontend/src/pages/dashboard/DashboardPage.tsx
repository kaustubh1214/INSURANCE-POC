import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { apiGet } from '@/services/api'
import type { Claim, PolicyEnrollment } from '@/types'

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  icon: string
  color: string
  to?: string
}

function StatCard({ label, value, sub, icon, color, to }: StatCardProps) {
  const card = (
    <div className={`bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition group`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center text-xl ${color}`}>
          {icon}
        </div>
        {to && (
          <span className="text-xs text-gray-400 group-hover:text-blue-600 transition">View →</span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm font-medium text-gray-600 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
  return to ? <Link to={to}>{card}</Link> : card
}

function ClaimStatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    draft:              'bg-gray-100 text-gray-600',
    submitted:          'bg-blue-100 text-blue-700',
    pending_documents:  'bg-yellow-100 text-yellow-700',
    under_review:       'bg-purple-100 text-purple-700',
    approved:           'bg-green-100 text-green-700',
    rejected:           'bg-red-100 text-red-700',
    settled:            'bg-emerald-100 text-emerald-700',
    withdrawn:          'bg-gray-100 text-gray-500',
  }
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${styles[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status.replace('_', ' ')}
    </span>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [claims, setClaims] = useState<Claim[]>([])
  const [enrollments, setEnrollments] = useState<PolicyEnrollment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [claimsRes, policiesRes] = await Promise.allSettled([
          apiGet<{ data: Claim[] }>('/claims/?limit=5'),
          apiGet<{ data: PolicyEnrollment[] }>('/policies/my-policies'),
        ])
        if (claimsRes.status === 'fulfilled' && claimsRes.value.data) {
          setClaims((claimsRes.value as any).data ?? [])
        }
        if (policiesRes.status === 'fulfilled' && policiesRes.value.data) {
          setEnrollments((policiesRes.value as any).data ?? [])
        }
      } catch {}
      setLoading(false)
    }
    load()
  }, [])

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const activeClaims   = claims.filter(c => !['settled', 'rejected', 'withdrawn'].includes(c.status))
  const pendingClaims  = claims.filter(c => c.status === 'pending_documents')
  const activePolicies = enrollments.filter(e => e.enrollment_status === 'active')

  return (
    <div>
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {greeting()}, {user?.full_name?.split(' ')[0]} 👋
        </h1>
        <p className="text-gray-500 mt-1 text-sm">
          Here's a summary of your benefits and claims activity.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon="📋" label="Active Policies" value={activePolicies.length}
          color="bg-blue-50" sub="Currently enrolled" to="/policies"
        />
        <StatCard
          icon="🗂️" label="Total Claims" value={claims.length}
          color="bg-purple-50" sub={`${activeClaims.length} in progress`} to="/claims"
        />
        <StatCard
          icon="⚠️" label="Pending Docs" value={pendingClaims.length}
          color="bg-yellow-50" sub="Action required"
        />
        <StatCard
          icon="✅" label="Settled Claims"
          value={claims.filter(c => c.status === 'settled').length}
          color="bg-green-50" sub="All time"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Claims */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h2 className="text-base font-semibold text-gray-800">Recent Claims</h2>
            <Link to="/claims" className="text-sm text-blue-600 hover:underline font-medium">
              View all →
            </Link>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
              Loading…
            </div>
          ) : claims.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-center px-6">
              <span className="text-4xl mb-3">🗂️</span>
              <p className="text-gray-500 text-sm font-medium">No claims yet</p>
              <p className="text-gray-400 text-xs mt-1">Submit your first claim from the Claims section.</p>
              <Link
                to="/claims"
                className="mt-3 text-sm text-blue-600 font-medium hover:underline"
              >
                Go to Claims →
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-50">
              {claims.slice(0, 5).map((claim) => (
                <div key={claim.id} className="flex items-center justify-between px-6 py-3.5 hover:bg-gray-50 transition">
                  <div>
                    <p className="text-sm font-semibold text-gray-800">{claim.claim_number}</p>
                    <p className="text-xs text-gray-400 capitalize mt-0.5">
                      {claim.claim_type.replace('_', ' ')}
                      {claim.hospital_name ? ` · ${claim.hospital_name}` : ''}
                    </p>
                  </div>
                  <div className="text-right flex items-center gap-3">
                    <div>
                      <p className="text-sm font-semibold text-gray-800">
                        ₹{Number(claim.claimed_amount).toLocaleString('en-IN')}
                      </p>
                      <p className="text-xs text-gray-400">
                        {new Date(claim.created_at).toLocaleDateString('en-IN')}
                      </p>
                    </div>
                    <ClaimStatusBadge status={claim.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions + Policies */}
        <div className="space-y-4">
          {/* Quick Actions */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              {[
                { to: '/claims',     label: 'File a Claim',          icon: '➕', color: 'text-blue-600 bg-blue-50' },
                { to: '/checkups',   label: 'Book Health Checkup',   icon: '🏥', color: 'text-green-600 bg-green-50' },
                { to: '/policies',   label: 'View My Policies',      icon: '📋', color: 'text-purple-600 bg-purple-50' },
                { to: '/health-card',label: 'My Health Card',        icon: '💳', color: 'text-orange-600 bg-orange-50' },
                { to: '/tickets',    label: 'Raise a Support Ticket',icon: '🎫', color: 'text-pink-600 bg-pink-50' },
              ].map((a) => (
                <Link
                  key={a.to}
                  to={a.to}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 transition"
                >
                  <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${a.color}`}>
                    {a.icon}
                  </span>
                  <span className="text-sm font-medium text-gray-700">{a.label}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Active Policies mini list */}
          {activePolicies.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h2 className="text-base font-semibold text-gray-800 mb-3">Active Policies</h2>
              <div className="space-y-2">
                {activePolicies.slice(0, 3).map((e) => (
                  <div key={e.id} className="flex items-center justify-between py-1">
                    <span className="text-sm text-gray-600 truncate">{e.policy_id}</span>
                    <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">
                      Active
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
