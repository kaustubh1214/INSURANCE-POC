import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '@/services/api'

interface Ticket {
  id: string
  ticket_number: string
  subject: string
  description: string
  category: string | null
  priority: string
  status: string
  ai_auto_resolved: boolean
  ai_resolution_suggestion: string | null
  satisfaction_rating: number | null
  created_at: string
  resolved_at: string | null
}

const PRIORITY_STYLES: Record<string, string> = {
  low:      'bg-gray-100 text-gray-500',
  medium:   'bg-blue-100 text-blue-600',
  high:     'bg-orange-100 text-orange-600',
  critical: 'bg-red-100 text-red-700',
}

const STATUS_STYLES: Record<string, string> = {
  open:            'bg-blue-100 text-blue-700',
  in_progress:     'bg-purple-100 text-purple-700',
  waiting_on_user: 'bg-yellow-100 text-yellow-700',
  resolved:        'bg-green-100 text-green-700',
  closed:          'bg-gray-100 text-gray-500',
}

function NewTicketModal({ onClose, onCreated }: {
  onClose: () => void
  onCreated: () => void
}) {
  const [form, setForm] = useState({
    subject: '',
    description: '',
    category: 'general',
    priority: 'medium',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.subject.trim()) { setError('Subject is required.'); return }
    if (!form.description.trim()) { setError('Description is required.'); return }
    setSubmitting(true)
    setError('')
    try {
      await apiPost('/tickets/', form)
      onCreated()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Failed to create ticket.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">Raise Support Ticket</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm rounded-xl px-4 py-2.5">⚠️ {error}</div>
          )}

          {/* AI suggestion hint */}
          <div className="bg-blue-50 rounded-xl px-4 py-3 text-xs text-blue-700">
            🤖 Our AI assistant will review your ticket and suggest a resolution instantly.
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Subject *</label>
            <input
              type="text"
              value={form.subject}
              onChange={e => set('subject', e.target.value)}
              placeholder="e.g. Unable to view my claim status"
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Category</label>
              <select
                value={form.category}
                onChange={e => set('category', e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
              >
                {[
                  ['claim_query',  'Claim Query'],
                  ['policy_query', 'Policy Query'],
                  ['payment',      'Payment'],
                  ['card_issue',   'Card Issue'],
                  ['enrollment',   'Enrollment'],
                  ['technical',    'Technical'],
                  ['general',      'General'],
                ].map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Priority</label>
              <select
                value={form.priority}
                onChange={e => set('priority', e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
              >
                {['low', 'medium', 'high', 'critical'].map(p => (
                  <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Description *</label>
            <textarea
              value={form.description}
              onChange={e => set('description', e.target.value)}
              rows={4}
              placeholder="Describe your issue in detail…"
              className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition">
              Cancel
            </button>
            <button type="submit" disabled={submitting}
              className="flex-1 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 disabled:bg-blue-300 text-white text-sm font-semibold transition">
              {submitting ? 'Submitting…' : 'Submit Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function TicketsPage() {
  const [tickets, setTickets]     = useState<Ticket[]>([])
  const [loading, setLoading]     = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [expanded, setExpanded]   = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const r = await apiGet<Ticket[]>('/tickets/')
      setTickets((r as any).data ?? [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const open     = tickets.filter(t => ['open', 'in_progress', 'waiting_on_user'].includes(t.status))
  const resolved = tickets.filter(t => ['resolved', 'closed'].includes(t.status))

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Tickets</h1>
          <p className="text-gray-500 text-sm mt-1">
            AI-assisted support — most tickets resolved instantly.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-sm font-semibold transition shadow-sm"
        >
          🎫 New Ticket
        </button>
      </div>

      {/* Stats */}
      {tickets.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Open', value: open.length, color: 'text-blue-700', bg: 'bg-blue-50' },
            { label: 'Resolved', value: resolved.length, color: 'text-green-700', bg: 'bg-green-50' },
            { label: 'AI Resolved', value: tickets.filter(t => t.ai_auto_resolved).length, color: 'text-purple-700', bg: 'bg-purple-50' },
          ].map(s => (
            <div key={s.label} className={`${s.bg} rounded-2xl p-4 text-center`}>
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-40 text-gray-400">Loading…</div>
      ) : tickets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl mb-4">🎫</span>
          <p className="text-gray-600 font-medium">No tickets raised</p>
          <p className="text-gray-400 text-sm mt-1">Have an issue? Our AI assistant will help you instantly.</p>
          <button onClick={() => setShowModal(true)}
            className="mt-4 px-5 py-2 bg-blue-700 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition">
            Raise a Ticket
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {tickets.map(t => (
            <div key={t.id}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition">
              {/* Header row */}
              <button
                onClick={() => setExpanded(expanded === t.id ? null : t.id)}
                className="w-full text-left p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl mt-0.5">
                    {t.ai_auto_resolved ? '🤖' : '🎫'}
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="font-mono text-xs text-gray-400">{t.ticket_number}</span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${PRIORITY_STYLES[t.priority]}`}>
                        {t.priority}
                      </span>
                      {t.ai_auto_resolved && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-700">
                          AI resolved
                        </span>
                      )}
                    </div>
                    <p className="font-semibold text-gray-900 text-sm">{t.subject}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(t.created_at).toLocaleDateString('en-IN')}
                      {t.category && ` · ${t.category.replace(/_/g, ' ')}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${STATUS_STYLES[t.status] ?? 'bg-gray-100 text-gray-600'}`}>
                    {t.status.replace(/_/g, ' ')}
                  </span>
                  <span className={`text-gray-400 text-sm transition-transform duration-200 ${expanded === t.id ? 'rotate-180' : ''}`}>
                    ▾
                  </span>
                </div>
              </button>

              {/* Expanded body */}
              {expanded === t.id && (
                <div className="px-5 pb-5 space-y-3 border-t border-gray-50 pt-4">
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Description</p>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{t.description}</p>
                  </div>

                  {t.ai_resolution_suggestion && (
                    <div className="bg-purple-50 rounded-xl p-4">
                      <p className="text-xs font-bold text-purple-700 mb-1.5">🤖 AI Suggested Resolution</p>
                      <p className="text-sm text-purple-700">{t.ai_resolution_suggestion}</p>
                    </div>
                  )}

                  {t.resolved_at && (
                    <p className="text-xs text-gray-400">
                      Resolved: {new Date(t.resolved_at).toLocaleString('en-IN')}
                    </p>
                  )}

                  {t.satisfaction_rating && (
                    <div className="flex items-center gap-1">
                      {[1,2,3,4,5].map(n => (
                        <span key={n} className={`text-lg ${n <= t.satisfaction_rating! ? 'text-yellow-400' : 'text-gray-200'}`}>★</span>
                      ))}
                      <span className="text-xs text-gray-400 ml-1">({t.satisfaction_rating}/5)</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <NewTicketModal onClose={() => setShowModal(false)} onCreated={load} />
      )}
    </div>
  )
}
