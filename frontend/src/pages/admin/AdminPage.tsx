import { useEffect, useState } from 'react'
import { apiGet, apiPut } from '@/services/api'

// Valid next-status transitions per current status
const NEXT_STATUSES: Record<string, string[]> = {
  draft:             ['submitted'],
  submitted:         ['under_review', 'rejected'],
  under_review:      ['approved', 'pending_documents', 'rejected'],
  pending_documents: ['under_review', 'rejected'],
  approved:          ['settled'],
  settled:           [],
  rejected:          [],
  withdrawn:         [],
}

const STATUS_STYLES: Record<string, string> = {
  draft:             'bg-gray-100 text-gray-600',
  submitted:         'bg-blue-100 text-blue-700',
  pending_documents: 'bg-yellow-100 text-yellow-700',
  under_review:      'bg-purple-100 text-purple-700',
  approved:          'bg-green-100 text-green-700',
  rejected:          'bg-red-100 text-red-700',
  settled:           'bg-emerald-100 text-emerald-700',
}

const STATUS_LABELS: Record<string, string> = {
  under_review:      'Under Review',
  pending_documents: 'Request Docs',
  approved:          'Approve',
  rejected:          'Reject',
  settled:           'Mark Settled',
  submitted:         'Re-submit',
}

// ── Update Status Modal ───────────────────────────────────────────────────────
function UpdateStatusModal({
  claim, onClose, onUpdated,
}: {
  claim: any
  onClose: () => void
  onUpdated: () => void
}) {
  const nextStatuses = NEXT_STATUSES[claim.status] ?? []
  const [newStatus,      setNewStatus]      = useState(nextStatuses[0] ?? '')
  const [approvedAmount, setApprovedAmount] = useState(String(claim.claimed_amount ?? ''))
  const [reason,         setReason]         = useState('')
  const [saving,         setSaving]         = useState(false)
  const [error,          setError]          = useState('')

  const handleSave = async () => {
    if (!newStatus) return
    setSaving(true)
    setError('')
    try {
      await apiPut(`/claims/${claim.id}/status`, {
        status:          newStatus,
        change_reason:   reason || null,
        approved_amount: newStatus === 'approved' ? Number(approvedAmount) : null,
      })
      onUpdated()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Update failed.')
    } finally {
      setSaving(false)
    }
  }

  if (nextStatuses.length === 0) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h2 className="font-bold text-gray-900">Update Claim Status</h2>
            <p className="text-xs text-gray-400 mt-0.5">{claim.claim_number}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <div className="px-6 py-5 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-2.5">⚠️ {error}</div>
          )}

          {/* Current status */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <div>
              <p className="text-xs text-gray-400 mb-1">Current Status</p>
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${STATUS_STYLES[claim.status] ?? 'bg-gray-100 text-gray-600'}`}>
                {claim.status?.replace(/_/g, ' ')}
              </span>
            </div>
            <span className="text-gray-300 text-lg">→</span>
            <div>
              <p className="text-xs text-gray-400 mb-1">New Status</p>
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${STATUS_STYLES[newStatus] ?? 'bg-gray-100 text-gray-600'}`}>
                {newStatus?.replace(/_/g, ' ')}
              </span>
            </div>
          </div>

          {/* Status select */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Change To *</label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {nextStatuses.map((s) => (
                <option key={s} value={s}>{s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
              ))}
            </select>
          </div>

          {/* Approved amount (only when approving) */}
          {newStatus === 'approved' && (
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Approved Amount (₹) *</label>
              <input
                type="number"
                value={approvedAmount}
                onChange={(e) => setApprovedAmount(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder={String(claim.claimed_amount)}
              />
              <p className="text-xs text-gray-400 mt-1">Claimed: ₹{Number(claim.claimed_amount).toLocaleString('en-IN')}</p>
            </div>
          )}

          {/* Reason */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              {newStatus === 'rejected' ? 'Rejection Reason *' : 'Note / Reason (optional)'}
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
              placeholder={newStatus === 'rejected' ? 'Explain why this claim is rejected…' : 'Add a note for audit trail…'}
            />
          </div>

          <div className="flex gap-3 pt-1">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !newStatus}
              className={`flex-1 py-2.5 rounded-xl text-white text-sm font-semibold transition disabled:opacity-50 ${
                newStatus === 'rejected' ? 'bg-red-600 hover:bg-red-700' :
                newStatus === 'approved' || newStatus === 'settled' ? 'bg-green-600 hover:bg-green-700' :
                'bg-blue-700 hover:bg-blue-800'
              }`}
            >
              {saving ? 'Saving…' : `Confirm: ${(newStatus || '').replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase())}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Admin Page ────────────────────────────────────────────────────────────────
export default function AdminPage() {
  const [claims, setClaims]     = useState<any[]>([])
  const [loading, setLoading]   = useState(true)
  const [updating, setUpdating] = useState<any | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const r = await apiGet<any[]>('/claims/?limit=100')
      setClaims((r as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const pending  = claims.filter(c => c.status === 'submitted' || c.status === 'under_review')
  const needDocs = claims.filter(c => c.status === 'pending_documents')

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-500 text-sm mt-1">Review claims and update their status.</p>
      </div>

      {/* Alert banners */}
      <div className="space-y-3 mb-6">
        {pending.length > 0 && (
          <div className="bg-purple-50 border border-purple-200 rounded-xl px-4 py-3 flex items-center gap-3">
            <span className="text-purple-500 text-xl">🔔</span>
            <p className="text-sm text-purple-700">
              <strong>{pending.length} claim(s)</strong> awaiting your review.
            </p>
          </div>
        )}
        {needDocs.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex items-center gap-3">
            <span className="text-yellow-500 text-xl">📄</span>
            <p className="text-sm text-yellow-700">
              <strong>{needDocs.length} claim(s)</strong> pending document submission from employees.
            </p>
          </div>
        )}
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { icon: '🗂️', label: 'Total Claims',   value: claims.length,                                      color: 'bg-blue-50' },
          { icon: '🔄', label: 'Pending Review',  value: pending.length,                                    color: 'bg-purple-50' },
          { icon: '⚠️', label: 'Pending Docs',    value: needDocs.length,                                   color: 'bg-yellow-50' },
          { icon: '✅', label: 'Settled',          value: claims.filter(c => c.status === 'settled').length, color: 'bg-green-50' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <div className={`w-11 h-11 ${s.color} rounded-xl flex items-center justify-center text-xl mb-3`}>{s.icon}</div>
            <p className="text-2xl font-bold text-gray-900">{s.value}</p>
            <p className="text-sm text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Claims table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-800">All Claims — Admin View</h2>
          <button onClick={load} className="text-xs text-blue-600 hover:text-blue-800 font-medium">↻ Refresh</button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
        ) : claims.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <span className="text-4xl mb-3">🗂️</span>
            <p className="text-gray-500">No claims in the system yet.</p>
            <p className="text-gray-400 text-sm mt-1">Claims filed by employees will appear here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {['Claim #','Type','Hospital','Amount','AI Fraud','Status','Action'].map(h => (
                    <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {claims.map((c: any) => {
                  const nextOpts = NEXT_STATUSES[c.status] ?? []
                  return (
                    <tr key={c.id} className="hover:bg-gray-50 transition">
                      <td className="px-5 py-4 font-mono text-xs text-gray-700 whitespace-nowrap">{c.claim_number}</td>
                      <td className="px-5 py-4 capitalize text-gray-600 whitespace-nowrap">{c.claim_type?.replace(/_/g,' ')}</td>
                      <td className="px-5 py-4 text-gray-600 max-w-[120px] truncate">{c.hospital_name ?? '—'}</td>
                      <td className="px-5 py-4 font-semibold text-gray-900 whitespace-nowrap">
                        ₹{Number(c.claimed_amount).toLocaleString('en-IN')}
                        {c.approved_amount != null && (
                          <span className="block text-xs text-green-600 font-normal">
                            ✓ ₹{Number(c.approved_amount).toLocaleString('en-IN')}
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {c.ai_fraud_score != null ? (
                          <div className="flex items-center gap-2">
                            <div className="w-14 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${c.ai_fraud_score > 0.6 ? 'bg-red-500' : c.ai_fraud_score > 0.3 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                style={{ width: `${c.ai_fraud_score * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500">{(c.ai_fraud_score * 100).toFixed(0)}%</span>
                          </div>
                        ) : <span className="text-gray-300 text-xs">—</span>}
                      </td>
                      <td className="px-5 py-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${STATUS_STYLES[c.status] ?? 'bg-gray-100 text-gray-600'}`}>
                          {c.status?.replace(/_/g,' ')}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        {nextOpts.length > 0 ? (
                          <button
                            onClick={() => setUpdating(c)}
                            className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg transition whitespace-nowrap"
                          >
                            Update Status →
                          </button>
                        ) : (
                          <span className="text-xs text-gray-300">Final</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {updating && (
        <UpdateStatusModal
          claim={updating}
          onClose={() => setUpdating(null)}
          onUpdated={load}
        />
      )}
    </div>
  )
}
