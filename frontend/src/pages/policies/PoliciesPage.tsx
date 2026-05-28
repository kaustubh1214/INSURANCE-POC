import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '@/services/api'
import type { Policy, PolicyEnrollment } from '@/types'

function PolicyTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    health:      'bg-blue-100 text-blue-700',
    life:        'bg-purple-100 text-purple-700',
    accidental:  'bg-red-100 text-red-700',
    dental:      'bg-orange-100 text-orange-700',
    vision:      'bg-teal-100 text-teal-700',
    term:        'bg-gray-100 text-gray-700',
  }
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${colors[type] ?? 'bg-gray-100 text-gray-600'}`}>
      {type}
    </span>
  )
}

function Toast({ msg, type }: { msg: string; type: 'success' | 'error' }) {
  return (
    <div className={`fixed top-6 right-6 z-50 px-5 py-3 rounded-xl shadow-lg text-sm font-semibold flex items-center gap-2 ${
      type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
    }`}>
      {type === 'success' ? '✅' : '⚠️'} {msg}
    </div>
  )
}

export default function PoliciesPage() {
  const [tab, setTab]               = useState<'enrolled' | 'available'>('enrolled')
  const [enrollments, setEnrollments] = useState<PolicyEnrollment[]>([])
  const [allPolicies, setAllPolicies] = useState<Policy[]>([])
  const [loading, setLoading]       = useState(true)
  const [enrollingId, setEnrollingId] = useState<string | null>(null)
  const [toast, setToast]           = useState<{ msg: string; type: 'success' | 'error' } | null>(null)

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const load = async () => {
    setLoading(true)
    try {
      const [myRes, allRes] = await Promise.allSettled([
        apiGet<PolicyEnrollment[]>('/policies/my-policies'),
        apiGet<Policy[]>('/policies/'),
      ])
      if (myRes.status === 'fulfilled') setEnrollments((myRes.value as any).data ?? [])
      if (allRes.status === 'fulfilled') setAllPolicies((allRes.value as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  // Build a set of already-enrolled policy IDs
  const enrolledPolicyIds = new Set(enrollments.map((e) => e.policy_id))

  // Look up policy name from allPolicies by policy_id
  const policyMap = Object.fromEntries(allPolicies.map((p) => [p.id, p]))

  const handleEnroll = async (policy: Policy) => {
    setEnrollingId(policy.id)
    try {
      const today = new Date().toISOString().split('T')[0]
      const endDate = policy.policy_end_date ?? '2025-12-31'
      await apiPost(`/policies/${policy.id}/enroll`, {
        policy_id:           policy.id,
        enrollment_date:     today,
        coverage_start_date: today,
        coverage_end_date:   endDate,
      })
      showToast(`Enrolled in ${policy.policy_name}!`, 'success')
      await load()                         // refresh both tabs
      setTab('enrolled')                   // switch to My Policies
    } catch (err: any) {
      const msg = err?.response?.data?.message ?? 'Enrollment failed. Try again.'
      showToast(msg, 'error')
    } finally {
      setEnrollingId(null)
    }
  }

  return (
    <div>
      {toast && <Toast msg={toast.msg} type={toast.type} />}

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Policies</h1>
        <p className="text-gray-500 text-sm mt-1">View your enrolled policies and available plans.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit mb-6">
        {(['enrolled', 'available'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition capitalize ${
              tab === t ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t === 'enrolled'
              ? `My Policies (${enrollments.length})`
              : `Available Plans (${allPolicies.length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
      ) : tab === 'enrolled' ? (
        /* ── MY POLICIES TAB ── */
        enrollments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-4">📋</span>
            <p className="text-gray-600 font-medium">Not enrolled in any policy</p>
            <p className="text-gray-400 text-sm mt-1 mb-4">Browse the Available Plans tab and click Enroll.</p>
            <button
              onClick={() => setTab('available')}
              className="px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition"
            >
              Browse Available Plans →
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {enrollments.map((e) => {
              const policy = policyMap[e.policy_id]
              return (
                <div key={e.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl">
                      {policy?.policy_type === 'life' ? '🛡️' : policy?.policy_type === 'accidental' ? '🚑' : '💊'}
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${
                      e.enrollment_status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                    }`}>
                      {e.enrollment_status}
                    </span>
                  </div>

                  {policy ? (
                    <>
                      <p className="font-bold text-gray-900 mb-0.5">{policy.policy_name}</p>
                      <p className="text-xs text-gray-400 mb-3">{policy.policy_number} · {policy.insurer_name}</p>
                      <div className="mb-3">
                        <PolicyTypeBadge type={policy.policy_type} />
                      </div>
                    </>
                  ) : (
                    <p className="text-xs text-gray-400 mb-3 font-mono">{e.policy_id}</p>
                  )}

                  <div className="grid grid-cols-2 gap-3 text-xs pt-3 border-t border-gray-50">
                    <div>
                      <p className="text-gray-400">Enrolled On</p>
                      <p className="font-semibold text-gray-700 mt-0.5">
                        {new Date(e.enrollment_date).toLocaleDateString('en-IN')}
                      </p>
                    </div>
                    {e.coverage_end_date && (
                      <div>
                        <p className="text-gray-400">Valid Until</p>
                        <p className="font-semibold text-gray-700 mt-0.5">
                          {new Date(e.coverage_end_date).toLocaleDateString('en-IN')}
                        </p>
                      </div>
                    )}
                    <div className="col-span-2">
                      <p className="text-gray-400">Sum Insured</p>
                      <p className="font-bold text-blue-700 mt-0.5 text-base">
                        ₹{Number(e.sum_insured ?? policy?.sum_insured ?? 0).toLocaleString('en-IN')}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )
      ) : (
        /* ── AVAILABLE PLANS TAB ── */
        allPolicies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-4">📭</span>
            <p className="text-gray-600 font-medium">No policies available</p>
            <p className="text-gray-400 text-sm mt-1">Check back later for available insurance plans.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {allPolicies.map((p) => {
              const isEnrolled = enrolledPolicyIds.has(p.id)
              const isEnrolling = enrollingId === p.id
              return (
                <div key={p.id} className={`bg-white rounded-2xl border shadow-sm p-5 flex flex-col transition ${
                  isEnrolled ? 'border-green-200' : 'border-gray-100 hover:shadow-md'
                }`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex gap-1.5 flex-wrap">
                      <PolicyTypeBadge type={p.policy_type} />
                      {p.is_corporate && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full">Corporate</span>
                      )}
                    </div>
                    <span className={`text-xs font-medium ${p.is_active ? 'text-green-600' : 'text-gray-400'}`}>
                      {p.is_active ? '● Active' : '○ Inactive'}
                    </span>
                  </div>

                  <h3 className="font-bold text-gray-900 mb-0.5">{p.policy_name}</h3>
                  <p className="text-xs text-gray-400 mb-3">{p.policy_number} · {p.insurer_name}</p>

                  {p.description && (
                    <p className="text-xs text-gray-500 mb-3 line-clamp-2">{p.description}</p>
                  )}

                  <div className="flex items-end justify-between pt-3 border-t border-gray-50 mb-3">
                    <div>
                      <p className="text-xs text-gray-400">Sum Insured</p>
                      <p className="font-bold text-blue-700">₹{Number(p.sum_insured).toLocaleString('en-IN')}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400">Premium</p>
                      <p className="font-semibold text-gray-700 text-sm">
                        ₹{Number(p.premium_amount).toLocaleString('en-IN')}/
                        {p.premium_frequency === 'annual' ? 'yr' : p.premium_frequency === 'monthly' ? 'mo' : 'qtr'}
                      </p>
                    </div>
                  </div>

                  {p.benefits_summary && (
                    <div className="mb-4">
                      <p className="text-xs text-gray-400 font-medium mb-1">Key Benefits</p>
                      <p className="text-xs text-gray-600 line-clamp-2">{p.benefits_summary}</p>
                    </div>
                  )}

                  {/* ── Enroll button ── */}
                  <div className="mt-auto">
                    {isEnrolled ? (
                      <div className="w-full py-2.5 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm font-semibold text-center">
                        ✅ Already Enrolled
                      </div>
                    ) : (
                      <button
                        onClick={() => handleEnroll(p)}
                        disabled={isEnrolling || !p.is_active}
                        className="w-full py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 disabled:bg-blue-300 text-white text-sm font-semibold transition"
                      >
                        {isEnrolling ? 'Enrolling…' : 'Enroll Now'}
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )
      )}
    </div>
  )
}
