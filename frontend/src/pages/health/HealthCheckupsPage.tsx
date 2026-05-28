import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '@/services/api'

interface LabPartner {
  id: string
  name: string
  city: string | null
  state: string | null
  phone: string | null
  is_home_collection: boolean
  rating: number | null
}

interface HealthCheckup {
  id: string
  checkup_type: string
  package_name: string | null
  scheduled_date: string | null
  preferred_date: string | null
  status: string
  is_home_collection: boolean
  report_url: string | null
  ai_health_summary: string | null
  follow_up_recommended: boolean
  created_at: string
}

const STATUS_STYLES: Record<string, string> = {
  booked:           'bg-blue-100 text-blue-700',
  confirmed:        'bg-indigo-100 text-indigo-700',
  sample_collected: 'bg-purple-100 text-purple-700',
  reports_uploaded: 'bg-orange-100 text-orange-700',
  completed:        'bg-green-100 text-green-700',
  cancelled:        'bg-red-100 text-red-700',
}

const STATUS_ICONS: Record<string, string> = {
  booked: '📅', confirmed: '✅', sample_collected: '🧪',
  reports_uploaded: '📄', completed: '🎉', cancelled: '❌',
}

function BookCheckupModal({ labs, onClose, onBooked }: {
  labs: LabPartner[]
  onClose: () => void
  onBooked: () => void
}) {
  const [form, setForm] = useState({
    checkup_type: 'annual_health_checkup',
    lab_partner_id: '',
    preferred_date: '',
    is_home_collection: false,
    package_name: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await apiPost('/health-checkups/', {
        ...form,
        lab_partner_id: form.lab_partner_id || null,
        preferred_date: form.preferred_date || null,
        package_name: form.package_name || null,
      })
      onBooked()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Booking failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">Book Health Checkup</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-2.5">⚠️ {error}</div>
          )}

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Checkup Type *</label>
            <select
              value={form.checkup_type}
              onChange={e => set('checkup_type', e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {[
                ['annual_health_checkup', 'Annual Health Checkup'],
                ['pre_policy',            'Pre-Policy Checkup'],
                ['follow_up',             'Follow-up'],
                ['diagnostics',           'Diagnostics'],
              ].map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Package Name</label>
            <input
              type="text"
              value={form.package_name}
              onChange={e => set('package_name', e.target.value)}
              placeholder="e.g. Comprehensive Health Package"
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Preferred Lab</label>
            <select
              value={form.lab_partner_id}
              onChange={e => set('lab_partner_id', e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="">— Auto-assign nearest lab —</option>
              {labs.map(l => (
                <option key={l.id} value={l.id}>
                  {l.name}{l.city ? ` · ${l.city}` : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Preferred Date</label>
            <input
              type="date"
              value={form.preferred_date}
              min={new Date().toISOString().split('T')[0]}
              onChange={e => set('preferred_date', e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_home_collection}
              onChange={e => set('is_home_collection', e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700">Home sample collection</span>
          </label>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition">
              Cancel
            </button>
            <button type="submit" disabled={submitting}
              className="flex-1 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 disabled:bg-blue-300 text-white text-sm font-semibold transition">
              {submitting ? 'Booking…' : 'Book Now'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function HealthCheckupsPage() {
  const [checkups, setCheckups] = useState<HealthCheckup[]>([])
  const [labs, setLabs]         = useState<LabPartner[]>([])
  const [loading, setLoading]   = useState(true)
  const [showModal, setShowModal] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [cu, lb] = await Promise.allSettled([
        apiGet<HealthCheckup[]>('/health-checkups/'),
        apiGet<LabPartner[]>('/health-checkups/labs'),
      ])
      if (cu.status === 'fulfilled') setCheckups((cu.value as any).data ?? [])
      if (lb.status === 'fulfilled') setLabs((lb.value as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Health Checkups</h1>
          <p className="text-gray-500 text-sm mt-1">Schedule and track your health screenings.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition shadow-sm"
        >
          📅 Book Checkup
        </button>
      </div>

      {/* How it works */}
      <div className="bg-blue-50 rounded-2xl p-5 mb-6">
        <h2 className="text-sm font-bold text-blue-800 mb-3">How it works</h2>
        <div className="flex flex-wrap gap-2">
          {[
            ['1', 'Book checkup'],
            ['2', 'Lab confirmed'],
            ['3', 'Sample collected'],
            ['4', 'Reports uploaded'],
            ['5', 'AI summary generated'],
          ].map(([n, l]) => (
            <div key={n} className="flex items-center gap-2 bg-white rounded-xl px-3 py-2 text-xs font-medium text-blue-700 shadow-sm">
              <span className="w-5 h-5 bg-blue-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                {n}
              </span>
              {l}
            </div>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
      ) : checkups.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl mb-4">🏥</span>
          <p className="text-gray-600 font-medium">No checkups scheduled</p>
          <p className="text-gray-400 text-sm mt-1">Book your annual health checkup to stay on top of your health.</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 px-5 py-2 bg-blue-700 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition"
          >
            Book Now
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {checkups.map(c => (
            <div key={c.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
                    {STATUS_ICONS[c.status] ?? '🏥'}
                  </div>
                  <div>
                    <p className="font-bold text-gray-900 capitalize">
                      {c.checkup_type.replace(/_/g, ' ')}
                    </p>
                    {c.package_name && (
                      <p className="text-xs text-gray-500">{c.package_name}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-0.5">
                      Booked {new Date(c.created_at).toLocaleDateString('en-IN')}
                      {c.scheduled_date && ` · Scheduled ${new Date(c.scheduled_date).toLocaleDateString('en-IN')}`}
                      {c.is_home_collection && ' · 🏠 Home collection'}
                    </p>
                  </div>
                </div>
                <span className={`px-3 py-1.5 rounded-full text-xs font-semibold capitalize flex-shrink-0 ${STATUS_STYLES[c.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {c.status.replace(/_/g, ' ')}
                </span>
              </div>

              {/* AI summary */}
              {c.ai_health_summary && (
                <div className="mt-4 p-3 bg-blue-50 rounded-xl">
                  <p className="text-xs font-semibold text-blue-700 mb-1">🤖 AI Health Summary</p>
                  <p className="text-xs text-blue-600">{c.ai_health_summary}</p>
                </div>
              )}

              {/* Follow-up badge */}
              {c.follow_up_recommended && (
                <div className="mt-3 flex items-center gap-2 text-orange-600 bg-orange-50 rounded-xl px-3 py-2 text-xs font-medium">
                  <span>⚕️</span> Follow-up diagnostic recommended
                </div>
              )}

              {/* Report link */}
              {c.report_url && (
                <div className="mt-3">
                  <a
                    href={c.report_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:underline font-medium"
                  >
                    📄 View Report
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <BookCheckupModal labs={labs} onClose={() => setShowModal(false)} onBooked={load} />
      )}
    </div>
  )
}
