import { useEffect, useState } from 'react'
import { apiDelete, apiGet, apiPost, apiPut } from '@/services/api'
import type { FamilyMember } from '@/types'

const RELATIONSHIP_ICONS: Record<string, string> = {
  spouse:  '💑',
  child:   '👶',
  parent:  '👴',
  sibling: '👥',
}

function AddMemberModal({
  onClose,
  onAdded,
}: {
  onClose: () => void
  onAdded: () => void
}) {
  const [form, setForm] = useState({
    full_name: '',
    relationship: 'spouse',
    date_of_birth: '',
    gender: '',
    aadhaar_number: '',
    is_covered_under_policy: true,
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.full_name.trim()) { setError('Full name is required.'); return }
    setSubmitting(true)
    setError('')
    try {
      await apiPost('/family/', {
        ...form,
        date_of_birth: form.date_of_birth || null,
        gender: form.gender || null,
        aadhaar_number: form.aadhaar_number || null,
      })
      onAdded()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Failed to add member.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">Add Family Member</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-2.5">⚠️ {error}</div>
          )}

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Full Name *</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => set('full_name', e.target.value)}
              placeholder="e.g. Priya Sharma"
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Relationship *</label>
              <select
                value={form.relationship}
                onChange={(e) => set('relationship', e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
              >
                {['spouse', 'child', 'parent', 'sibling'].map((r) => (
                  <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Gender</label>
              <select
                value={form.gender}
                onChange={(e) => set('gender', e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="">Select…</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Date of Birth</label>
            <input
              type="date"
              value={form.date_of_birth}
              onChange={(e) => set('date_of_birth', e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Aadhaar Number</label>
            <input
              type="text"
              value={form.aadhaar_number}
              onChange={(e) => set('aadhaar_number', e.target.value)}
              placeholder="XXXX XXXX XXXX"
              maxLength={14}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none font-mono"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="covered"
              checked={form.is_covered_under_policy}
              onChange={(e) => set('is_covered_under_policy', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <label htmlFor="covered" className="text-sm text-gray-700">
              Include in policy coverage
            </label>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 disabled:bg-blue-300 text-white text-sm font-semibold transition"
            >
              {submitting ? 'Adding…' : 'Add Member'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function FamilyPage() {
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [loading, setLoading]  = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await apiGet<FamilyMember[]>('/family/')
      setMembers((res as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Remove this family member?')) return
    setDeleting(id)
    try {
      await apiDelete(`/family/${id}`)
      await load()
    } finally {
      setDeleting(null)
    }
  }

  const coveredCount   = members.filter((m) => m.is_covered_under_policy).length
  const uncoveredCount = members.length - coveredCount

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Family Members</h1>
          <p className="text-gray-500 text-sm mt-1">
            Manage dependents covered under your insurance.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition shadow-sm"
        >
          ➕ Add Member
        </button>
      </div>

      {/* Summary cards */}
      {members.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Total Members', value: members.length, icon: '👨‍👩‍👧', color: 'bg-blue-50' },
            { label: 'Covered',       value: coveredCount,   icon: '✅',    color: 'bg-green-50' },
            { label: 'Uncovered',     value: uncoveredCount, icon: '⚠️',   color: 'bg-yellow-50' },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-2xl border border-gray-100 p-4 text-center shadow-sm">
              <span className={`inline-flex items-center justify-center w-10 h-10 rounded-xl text-xl mb-2 ${s.color}`}>
                {s.icon}
              </span>
              <p className="text-xl font-bold text-gray-900">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Members grid */}
      {loading ? (
        <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
      ) : members.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl mb-4">👨‍👩‍👧</span>
          <p className="text-gray-600 font-medium">No family members added</p>
          <p className="text-gray-400 text-sm mt-1">Add your dependents to include them in your coverage.</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-5 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition"
          >
            Add First Member
          </button>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {members.map((m) => (
            <div key={m.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center text-2xl">
                    {RELATIONSHIP_ICONS[m.relationship] ?? '👤'}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 leading-tight">{m.full_name}</h3>
                    <p className="text-xs text-gray-400 capitalize">{m.relationship}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(m.id)}
                  disabled={deleting === m.id}
                  className="text-gray-300 hover:text-red-400 transition text-lg leading-none disabled:opacity-50"
                  title="Remove"
                >
                  {deleting === m.id ? '…' : '✕'}
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                {m.gender && (
                  <div>
                    <span className="text-gray-400">Gender</span>
                    <p className="font-medium capitalize">{m.gender}</p>
                  </div>
                )}
                {m.date_of_birth && (
                  <div>
                    <span className="text-gray-400">DOB</span>
                    <p className="font-medium">
                      {new Date(m.date_of_birth).toLocaleDateString('en-IN')}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-3 pt-3 border-t border-gray-50 flex items-center justify-between">
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                  m.is_covered_under_policy
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {m.is_covered_under_policy ? '✓ Covered' : '✗ Not Covered'}
                </span>
                <span className={`text-xs ${m.is_active ? 'text-gray-400' : 'text-red-400'}`}>
                  {m.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <AddMemberModal onClose={() => setShowModal(false)} onAdded={load} />
      )}
    </div>
  )
}
