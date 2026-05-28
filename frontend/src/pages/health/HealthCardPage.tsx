import { useEffect, useState } from 'react'
import { apiGet } from '@/services/api'
import { useAuthStore } from '@/store/authStore'

interface HealthCard {
  id: string
  card_number: string
  insurer_name: string
  plan_name: string | null
  network_type: string | null
  valid_from: string
  valid_to: string
  sum_insured: string | null
  tpa_name: string | null
  tpa_helpline: string | null
  tpa_email: string | null
  emergency_contact: string | null
  card_status: string
}

function InfoRow({ label, value }: { label: string; value: string | null }) {
  if (!value) return null
  return (
    <div>
      <p className="text-xs text-gray-400 mb-0.5">{label}</p>
      <p className="text-sm font-semibold text-gray-800">{value}</p>
    </div>
  )
}

export default function HealthCardPage() {
  const { user } = useAuthStore()
  const [card, setCard] = useState<HealthCard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiGet<HealthCard>('/health-cards/my-card')
      .then((r) => setCard((r as any).data ?? null))
      .catch(() => setError('No health card found for your account.'))
      .finally(() => setLoading(false))
  }, [])

  const isExpired = card
    ? new Date(card.valid_to) < new Date()
    : false

  const daysLeft = card
    ? Math.ceil((new Date(card.valid_to).getTime() - Date.now()) / 86_400_000)
    : 0

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Health Card</h1>
        <p className="text-gray-500 text-sm mt-1">Your digital insurance health card.</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-gray-400">Loading…</div>
      ) : error || !card ? (
        /* ── Empty / not-issued state ── */
        <div className="flex flex-col items-center justify-center py-24 text-center bg-white rounded-2xl border border-gray-100">
          <span className="text-6xl mb-4">💳</span>
          <p className="text-gray-700 font-semibold text-lg">No Health Card Issued</p>
          <p className="text-gray-400 text-sm mt-2 max-w-xs">
            Your health card will appear here once your HR team generates it after policy enrollment.
          </p>
        </div>
      ) : (
        <div className="max-w-2xl space-y-5">
          {/* ── Card visual ── */}
          <div className={`relative rounded-3xl overflow-hidden shadow-xl text-white
            ${isExpired
              ? 'bg-gradient-to-br from-gray-500 to-gray-700'
              : 'bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800'}`}
          >
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-white/5 -translate-y-1/2 translate-x-1/4" />
            <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full bg-white/5 translate-y-1/2 -translate-x-1/4" />

            <div className="relative p-7">
              {/* Top row */}
              <div className="flex items-start justify-between mb-8">
                <div>
                  <p className="text-blue-200 text-xs font-medium uppercase tracking-widest mb-1">
                    Health Insurance Card
                  </p>
                  <p className="text-xl font-bold">{card.insurer_name}</p>
                  {card.plan_name && (
                    <p className="text-blue-200 text-sm mt-0.5">{card.plan_name}</p>
                  )}
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center text-2xl">
                  💳
                </div>
              </div>

              {/* Card number */}
              <div className="mb-6">
                <p className="text-blue-300 text-xs mb-1">Card Number</p>
                <p className="text-2xl font-mono font-bold tracking-widest">
                  {card.card_number}
                </p>
              </div>

              {/* Bottom row */}
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-blue-300 text-xs mb-1">Card Holder</p>
                  <p className="font-semibold">{user?.full_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-blue-300 text-xs mb-1">Valid Thru</p>
                  <p className="font-semibold">
                    {new Date(card.valid_to).toLocaleDateString('en-IN', {
                      month: '2-digit', year: 'numeric',
                    })}
                  </p>
                </div>
                {card.sum_insured && (
                  <div className="text-right">
                    <p className="text-blue-300 text-xs mb-1">Sum Insured</p>
                    <p className="font-semibold">₹{card.sum_insured}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ── Status banner ── */}
          {isExpired ? (
            <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 flex items-center gap-3">
              <span className="text-red-500 text-lg">⚠️</span>
              <p className="text-sm text-red-700 font-medium">
                This health card expired on {new Date(card.valid_to).toLocaleDateString('en-IN')}.
                Please contact HR for renewal.
              </p>
            </div>
          ) : daysLeft <= 30 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex items-center gap-3">
              <span className="text-yellow-500 text-lg">⏰</span>
              <p className="text-sm text-yellow-700 font-medium">
                Your card expires in <strong>{daysLeft} days</strong>. Contact HR to arrange renewal.
              </p>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 flex items-center gap-3">
              <span className="text-green-500 text-lg">✅</span>
              <p className="text-sm text-green-700 font-medium">
                Card is active — valid for <strong>{daysLeft} more days</strong>.
              </p>
            </div>
          )}

          {/* ── Details grid ── */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wider">Card Details</h2>
            <div className="grid grid-cols-2 gap-x-8 gap-y-4">
              <InfoRow label="Network Type"  value={card.network_type} />
              <InfoRow label="Card Status"   value={card.card_status}  />
              <InfoRow label="Valid From"
                value={new Date(card.valid_from).toLocaleDateString('en-IN')} />
              <InfoRow label="Valid To"
                value={new Date(card.valid_to).toLocaleDateString('en-IN')} />
            </div>
          </div>

          {/* ── TPA Details ── */}
          {(card.tpa_name || card.tpa_helpline || card.tpa_email || card.emergency_contact) && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wider">
                TPA &amp; Emergency Contacts
              </h2>
              <div className="grid grid-cols-2 gap-x-8 gap-y-4">
                <InfoRow label="TPA Name"          value={card.tpa_name} />
                <InfoRow label="TPA Helpline"      value={card.tpa_helpline} />
                <InfoRow label="TPA Email"         value={card.tpa_email} />
                <InfoRow label="Emergency Contact" value={card.emergency_contact} />
              </div>
            </div>
          )}

          {/* ── Print hint ── */}
          <p className="text-xs text-gray-400 text-center pb-2">
            💡 Screenshot or print this page to carry a physical copy of your health card.
          </p>
        </div>
      )}
    </div>
  )
}
