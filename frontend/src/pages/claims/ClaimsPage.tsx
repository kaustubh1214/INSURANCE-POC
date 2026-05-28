import { useEffect, useState } from 'react'
import { apiGet, apiPost, apiPut } from '@/services/api'
import type { Claim, ClaimStatusHistory, Policy, PolicyEnrollment } from '@/types'

// ── Helpers ──────────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    draft:             'bg-gray-100 text-gray-600',
    submitted:         'bg-blue-100 text-blue-700',
    pending_documents: 'bg-yellow-100 text-yellow-700',
    under_review:      'bg-purple-100 text-purple-700',
    approved:          'bg-green-100 text-green-700',
    rejected:          'bg-red-100 text-red-700',
    settled:           'bg-emerald-100 text-emerald-700',
    withdrawn:         'bg-gray-100 text-gray-400',
  }
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${styles[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}

// ─── IMPORTANT: defined at module level so React never remounts it on re-render ───
function FormField({
  label, name, type = 'text', placeholder = '', value, onChange, required = false
}: {
  label: string; name: string; type?: string; placeholder?: string
  value: string; onChange: (v: string) => void; required?: boolean
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 mb-1">
        {label}{required && ' *'}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
      />
    </div>
  )
}

// ── Timeline drawer ──────────────────────────────────────────────────────────
function TimelineDrawer({ claim, onClose }: { claim: Claim; onClose: () => void }) {
  const [history, setHistory] = useState<ClaimStatusHistory[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiGet<ClaimStatusHistory[]>(`/claims/${claim.id}/timeline`)
      .then((r) => setHistory((r as any).data ?? []))
      .finally(() => setLoading(false))
  }, [claim.id])

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <aside className="w-full max-w-md bg-white h-full shadow-2xl overflow-y-auto flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h2 className="font-bold text-gray-900">{claim.claim_number}</h2>
            <p className="text-xs text-gray-400 capitalize mt-0.5">{claim.claim_type.replace(/_/g,' ')}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <div className="px-6 py-4 border-b border-gray-50 grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-xs text-gray-400">Claimed Amount</p>
            <p className="font-bold text-gray-900">₹{Number(claim.claimed_amount).toLocaleString('en-IN')}</p>
          </div>
          {claim.approved_amount != null && (
            <div>
              <p className="text-xs text-gray-400">Approved Amount</p>
              <p className="font-bold text-green-700">₹{Number(claim.approved_amount).toLocaleString('en-IN')}</p>
            </div>
          )}
          <div>
            <p className="text-xs text-gray-400">Status</p>
            <StatusBadge status={claim.status} />
          </div>
          {claim.hospital_name && (
            <div>
              <p className="text-xs text-gray-400">Hospital</p>
              <p className="font-medium text-gray-700 text-xs">{claim.hospital_name}</p>
            </div>
          )}
          {claim.diagnosis && (
            <div className="col-span-2">
              <p className="text-xs text-gray-400">Diagnosis</p>
              <p className="font-medium text-gray-700 text-xs">{claim.diagnosis}</p>
            </div>
          )}
          {claim.ai_summary && (
            <div className="col-span-2 mt-1 p-3 bg-blue-50 rounded-xl">
              <p className="text-xs font-semibold text-blue-700 mb-1">🤖 AI Summary</p>
              <p className="text-xs text-blue-600">{claim.ai_summary}</p>
            </div>
          )}
          {claim.ai_missing_docs && (
            <div className="col-span-2 p-3 bg-yellow-50 rounded-xl">
              <p className="text-xs font-semibold text-yellow-700 mb-1">⚠️ Missing Documents</p>
              <p className="text-xs text-yellow-600">{claim.ai_missing_docs}</p>
            </div>
          )}
        </div>

        <div className="px-6 py-4 flex-1">
          <p className="text-sm font-semibold text-gray-700 mb-4">Status Timeline</p>
          {loading ? (
            <p className="text-gray-400 text-sm">Loading…</p>
          ) : history.length === 0 ? (
            <p className="text-gray-400 text-sm">No history yet.</p>
          ) : (
            <ol className="relative border-l border-gray-200 space-y-4 ml-2">
              {history.map((h) => (
                <li key={h.id} className="ml-5">
                  <span className="absolute -left-2 flex items-center justify-center w-4 h-4 bg-blue-100 rounded-full ring-2 ring-white">
                    <span className="w-2 h-2 rounded-full bg-blue-600" />
                  </span>
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center justify-between mb-1">
                      <StatusBadge status={h.to_status} />
                      {h.is_system_action && <span className="text-xs text-gray-400">🤖 Auto</span>}
                    </div>
                    <p className="text-xs text-gray-500">{new Date(h.changed_at).toLocaleString('en-IN')}</p>
                    {h.changed_by_name && <p className="text-xs text-gray-600 mt-0.5">By: {h.changed_by_name}</p>}
                    {h.change_reason && <p className="text-xs text-gray-500 mt-0.5 italic">{h.change_reason}</p>}
                  </div>
                </li>
              ))}
            </ol>
          )}
        </div>
      </aside>
    </div>
  )
}

// ── New Claim Modal ──────────────────────────────────────────────────────────
function NewClaimModal({
  enrollments, policies, onClose, onCreated,
}: {
  enrollments: PolicyEnrollment[]
  policies: Policy[]
  onClose: () => void
  onCreated: () => void
}) {
  const [enrollmentId,       setEnrollmentId]       = useState(enrollments[0]?.id ?? '')
  const [claimType,          setClaimType]          = useState('hospitalization')
  const [hospitalName,       setHospitalName]       = useState('')
  const [diagnosis,          setDiagnosis]          = useState('')
  const [claimedAmount,      setClaimedAmount]      = useState('')
  const [treatmentStartDate, setTreatmentStartDate] = useState('')
  const [treatmentEndDate,   setTreatmentEndDate]   = useState('')
  const [notes,              setNotes]              = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError]           = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!enrollmentId)              { setError('Please select a policy enrollment.'); return }
    if (!claimedAmount || isNaN(Number(claimedAmount))) { setError('Enter a valid claim amount.'); return }

    setSubmitting(true)
    setError('')
    try {
      // Step 1: Create claim (DRAFT)
      const res: any = await apiPost('/claims/', {
        enrollment_id:        enrollmentId,
        claim_type:           claimType,
        hospital_name:        hospitalName || null,
        diagnosis:            diagnosis || null,
        claimed_amount:       Number(claimedAmount),
        treatment_start_date: treatmentStartDate || null,
        treatment_end_date:   treatmentEndDate || null,
        notes:                notes || null,
      })
      const claimId = res?.data?.id
      // Step 2: Auto-submit (DRAFT → SUBMITTED)
      if (claimId) {
        await apiPost(`/claims/${claimId}/submit`, {})
      }
      onCreated()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Failed to file claim. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">File New Claim</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-2.5 flex gap-2">
              <span>⚠️</span>{error}
            </div>
          )}

          {/* Policy Enrollment */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Policy Enrollment *</label>
            <select
              value={enrollmentId}
              onChange={(e) => setEnrollmentId(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {enrollments.length === 0 ? (
                <option value="">— No enrollments. Go to Policies first. —</option>
              ) : (
                enrollments.map((e) => {
                  const pol = policies.find((p) => p.id === e.policy_id)
                  return (
                    <option key={e.id} value={e.id}>
                      {pol ? `${pol.policy_name} (${pol.insurer_name})` : e.policy_id}
                    </option>
                  )
                })
              )}
            </select>
          </div>

          {/* Claim Type */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Claim Type *</label>
            <select
              value={claimType}
              onChange={(e) => setClaimType(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {['hospitalization','outpatient','dental','vision','pharmacy','accident'].map((t) => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>

          <FormField
            label="Hospital / Clinic Name" name="hospital_name"
            placeholder="e.g. Apollo Hospital, Mumbai"
            value={hospitalName} onChange={setHospitalName}
          />
          <FormField
            label="Diagnosis / Reason" name="diagnosis"
            placeholder="e.g. Acute Appendicitis"
            value={diagnosis} onChange={setDiagnosis}
          />
          <FormField
            label="Claim Amount (₹)" name="claimed_amount" type="number"
            placeholder="e.g. 85000"
            value={claimedAmount} onChange={setClaimedAmount} required
          />

          <div className="grid grid-cols-2 gap-3">
            <FormField
              label="Treatment Start" name="treatment_start_date" type="date"
              value={treatmentStartDate} onChange={setTreatmentStartDate}
            />
            <FormField
              label="Treatment End" name="treatment_end_date" type="date"
              value={treatmentEndDate} onChange={setTreatmentEndDate}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
              placeholder="Any additional information…"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button" onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || enrollments.length === 0}
              className="flex-1 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 disabled:bg-blue-300 text-white text-sm font-semibold transition"
            >
              {submitting ? 'Filing Claim…' : 'Submit Claim'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Main Claims Page ─────────────────────────────────────────────────────────
export default function ClaimsPage() {
  const [claims, setClaims]             = useState<Claim[]>([])
  const [enrollments, setEnrollments]   = useState<PolicyEnrollment[]>([])
  const [policies, setPolicies]         = useState<Policy[]>([])
  const [loading, setLoading]           = useState(true)
  const [showNewModal, setShowNewModal] = useState(false)
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null)
  const [filterStatus, setFilterStatus] = useState('all')

  const load = async () => {
    setLoading(true)
    try {
      const [claimsRes, enrollRes, policiesRes] = await Promise.allSettled([
        apiGet<Claim[]>('/claims/?limit=100'),
        apiGet<PolicyEnrollment[]>('/policies/my-policies'),
        apiGet<Policy[]>('/policies/'),
      ])
      if (claimsRes.status === 'fulfilled')   setClaims((claimsRes.value as any).data ?? [])
      if (enrollRes.status === 'fulfilled')   setEnrollments((enrollRes.value as any).data ?? [])
      if (policiesRes.status === 'fulfilled') setPolicies((policiesRes.value as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const filtered = filterStatus === 'all' ? claims : claims.filter(c => c.status === filterStatus)
  const statuses = ['all','draft','submitted','pending_documents','under_review','approved','settled','rejected']

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Claims</h1>
          <p className="text-gray-500 text-sm mt-1">Track and manage your insurance claims.</p>
        </div>
        <button
          onClick={() => setShowNewModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition shadow-sm"
        >
          ➕ File New Claim
        </button>
      </div>

      {/* Status filter pills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {statuses.map((s) => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition capitalize ${
              filterStatus === s
                ? 'bg-blue-700 text-white shadow'
                : 'bg-white border border-gray-200 text-gray-500 hover:border-blue-300'
            }`}
          >
            {s === 'all' ? `All (${claims.length})` : s.replace(/_/g,' ')}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl mb-4">🗂️</span>
          <p className="text-gray-600 font-medium">No claims found</p>
          <p className="text-gray-400 text-sm mt-1">
            {filterStatus === 'all' ? 'File your first claim using the button above.' : 'No claims with this status.'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {['Claim #','Type','Hospital','Amount','Date','Status',''].map((h) => (
                    <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((claim) => (
                  <tr key={claim.id} className="hover:bg-gray-50 transition">
                    <td className="px-5 py-4 font-mono text-xs font-semibold text-gray-700 whitespace-nowrap">{claim.claim_number}</td>
                    <td className="px-5 py-4 capitalize text-gray-600 whitespace-nowrap">{claim.claim_type.replace(/_/g,' ')}</td>
                    <td className="px-5 py-4 text-gray-600 max-w-[140px] truncate">{claim.hospital_name ?? '—'}</td>
                    <td className="px-5 py-4 font-semibold text-gray-900 whitespace-nowrap">
                      ₹{Number(claim.claimed_amount).toLocaleString('en-IN')}
                      {claim.approved_amount != null && (
                        <span className="block text-xs text-green-600 font-normal">
                          Approved: ₹{Number(claim.approved_amount).toLocaleString('en-IN')}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-gray-500 text-xs whitespace-nowrap">{new Date(claim.created_at).toLocaleDateString('en-IN')}</td>
                    <td className="px-5 py-4"><StatusBadge status={claim.status} /></td>
                    <td className="px-5 py-4">
                      <button
                        onClick={() => setSelectedClaim(claim)}
                        className="text-blue-600 hover:text-blue-800 text-xs font-medium whitespace-nowrap"
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showNewModal && (
        <NewClaimModal
          enrollments={enrollments}
          policies={policies}
          onClose={() => setShowNewModal(false)}
          onCreated={load}
        />
      )}
      {selectedClaim && (
        <TimelineDrawer claim={selectedClaim} onClose={() => setSelectedClaim(null)} />
      )}
    </div>
  )
}
