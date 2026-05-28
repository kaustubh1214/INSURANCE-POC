/**
 * Core TypeScript interfaces matching the backend Pydantic schemas.
 * Update these when adding new API fields.
 */

// ---------------------------------------------------------------------------
// API Response Envelope
// ---------------------------------------------------------------------------
export interface APIResponse<T> {
  success: boolean
  data: T | null
  message: string
  error_code?: string
  meta?: {
    request_id?: string
    page?: number
    page_size?: number
    total?: number
    total_pages?: number
  }
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface CurrentUser {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_verified: boolean
}

export type UserRole = 'admin' | 'hr' | 'employee' | 'insurer' | 'agent'

// ---------------------------------------------------------------------------
// Employee
// ---------------------------------------------------------------------------
export interface Employee {
  id: string
  user_id: string
  employee_code: string
  department: string | null
  designation: string | null
  date_of_joining: string | null
  employment_status: string
  company_name: string | null
  city: string | null
  state: string | null
  is_active: boolean
}

// ---------------------------------------------------------------------------
// Family Member
// ---------------------------------------------------------------------------
export interface FamilyMember {
  id: string
  employee_id: string
  full_name: string
  relationship: string
  date_of_birth: string | null
  gender: string | null
  is_covered_under_policy: boolean
  is_active: boolean
}

// ---------------------------------------------------------------------------
// Policy
// ---------------------------------------------------------------------------
export interface Policy {
  id: string
  policy_number: string
  policy_name: string
  policy_type: string
  insurer_name: string
  premium_amount: number
  sum_insured: number
  premium_frequency: string
  policy_start_date: string | null
  policy_end_date: string | null
  description: string | null
  benefits_summary: string | null
  max_family_members: number
  is_corporate: boolean
  is_active: boolean
}

export interface PolicyEnrollment {
  id: string
  employee_id: string
  policy_id: string
  enrollment_date: string
  coverage_start_date: string | null
  coverage_end_date: string | null
  enrollment_status: string
  sum_insured: number | null
  certificate_number: string | null
}

// ---------------------------------------------------------------------------
// Claims
// ---------------------------------------------------------------------------
export type ClaimStatus =
  | 'draft'
  | 'submitted'
  | 'pending_documents'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'settled'
  | 'withdrawn'

export interface Claim {
  id: string
  claim_number: string
  employee_id: string
  enrollment_id: string
  claim_type: string
  status: ClaimStatus
  claimed_amount: number
  approved_amount: number | null
  settled_amount: number | null
  diagnosis: string | null
  hospital_name: string | null
  treatment_start_date: string | null
  treatment_end_date: string | null
  patient_type: string
  ai_fraud_score: number | null
  ai_priority_score: number | null
  ai_category: string | null
  ai_summary: string | null
  ai_missing_docs: string | null
  submitted_at: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ClaimDocument {
  id: string
  claim_id: string
  document_type: string
  file_name: string
  ocr_status: string
  is_verified: boolean
  created_at: string
}

export interface ClaimStatusHistory {
  id: string
  from_status: string | null
  to_status: string
  changed_at: string
  changed_by_name: string | null
  change_reason: string | null
  is_system_action: boolean
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------
export interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  is_read: boolean
  read_at: string | null
  action_url: string | null
  created_at: string
}
