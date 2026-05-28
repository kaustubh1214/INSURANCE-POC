# PROJECT_CONTEXT.md
> **Living document** — updated after every major change. Always read this first before continuing development.

---

## 1. Project Overview

**Name:** InsureBridge — Enterprise Insurance & Employee Benefits Platform  
**Type:** Production-oriented Proof of Concept (POC)  
**Goal:** Showcase an AI-enabled, scalable, enterprise-grade platform for the Insurance & Employee Benefits sector — suitable for client presentation and future production expansion.

---

## 2. Tech Stack Decisions

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend API | FastAPI (Python 3.11+) | Async-first, typed, auto-docs (OpenAPI), AI-friendly |
| Database | SQLite (dev/POC) → PostgreSQL (prod) | Zero-config for POC, SQLAlchemy ORM makes migration trivial |
| ORM | SQLAlchemy 2.x + Alembic | Industry standard, async support, migration tracking |
| Frontend | React 18 + Vite + TypeScript | Fast dev, strong typing, component reuse |
| Styling | TailwindCSS + shadcn/ui | Rapid enterprise UI, accessible components |
| Auth | JWT (python-jose) + bcrypt | Stateless, role-aware, production-ready |
| AI Layer | Python service (LangChain + OpenAI/Anthropic) | Modular, swappable LLM provider |
| OCR | Tesseract + pytesseract / AWS Textract (pluggable) | Structured extraction from documents |
| Vector DB | ChromaDB (local dev) → Pinecone/Weaviate (prod) | Semantic search for policies, claims |
| Task Queue | FastAPI BackgroundTasks → Celery (prod) | Async processing for OCR, AI calls |
| Containerization | Docker + docker-compose | Consistent environments |
| API Docs | FastAPI auto-generated Swagger + ReDoc | Zero-effort documentation |

---

## 3. Architecture Decisions

### 3.1 Repository Pattern
All database access goes through **Repository classes** — no direct ORM queries in routers.  
`Router → Service → Repository → SQLAlchemy Model`

### 3.2 Module Structure
Each domain module contains:
- `models.py` — SQLAlchemy ORM models
- `schemas.py` — Pydantic request/response schemas
- `repository.py` — DB CRUD operations
- `service.py` — Business logic
- `router.py` — FastAPI route definitions

### 3.3 AI Services Isolation
All AI calls live in `/ai_services/` — never mixed with business logic. This enables:
- Easy model swapping
- Rate limiting / quota management
- AI audit logging
- PII masking before LLM calls

### 3.4 Security Design
- JWT tokens with role claims (admin, employee, insurer, agent, hr)
- Role-based decorators on every protected endpoint
- PII fields masked before any AI call
- All AI interactions logged to `ai_audit_log` table
- Input sanitization middleware
- Secrets via environment variables only

### 3.5 Database Strategy
- SQLite for POC (single file, zero config)
- SQLAlchemy ORM abstracts the DB engine
- Alembic for schema migrations
- Switch to PostgreSQL: change `DATABASE_URL` env var only

---

## 4. Module Status

| Module | Status | Notes |
|--------|--------|-------|
| Project Scaffolding | ✅ Complete | Folder structure created |
| Architecture Docs | ✅ Complete | This file + SYSTEM_ARCHITECTURE.md |
| Database Models | ✅ Complete | All 15 models defined |
| Authentication | ✅ Complete | JWT + RBAC implemented |
| User Management | ✅ Complete | CRUD + role assignment |
| Employee Management | ✅ Complete | Employee profile, HR linkage |
| Family Member Mgmt | ✅ Complete | Dependent management |
| Policy Management | ✅ Complete | Multi-policy per employee |
| Health Card | ✅ Complete | Card generation + access + UI |
| Claims Management | ✅ Complete | Full intimation workflow + UI |
| Ticketing System | ✅ Complete | Backend router + full UI |
| Health Checkup | ✅ Complete | Backend router + booking UI |
| React Frontend | ✅ Complete | 9 pages, sidebar, auth, routing |
| Admin Dashboard | ✅ Complete | Claims overview + AI score display |
| Docker Setup | ✅ Complete | docker-compose configured |
| AI Claim Assistant | 🔲 Pending | Phase 3 |
| OCR Pipeline | 🔲 Pending | Phase 3 |
| Notification Engine | 🔲 Pending | Phase 3 |
| AI Recommendation | 🔲 Pending | Phase 3 |
| RAG Chatbot (Support) | 🔲 Pending | Phase 3 |

---

## 5. APIs Created

### Auth
- `POST /api/v1/auth/register` — Register new user
- `POST /api/v1/auth/login` — Login, returns JWT
- `POST /api/v1/auth/refresh` — Refresh token
- `GET  /api/v1/auth/me` — Get current user

### Users
- `GET    /api/v1/users/` — List users (admin)
- `GET    /api/v1/users/{id}` — Get user
- `PUT    /api/v1/users/{id}` — Update user
- `DELETE /api/v1/users/{id}` — Soft-delete user

### Employees
- `POST   /api/v1/employees/` — Create employee profile
- `GET    /api/v1/employees/` — List employees
- `GET    /api/v1/employees/{id}` — Get employee
- `PUT    /api/v1/employees/{id}` — Update employee
- `GET    /api/v1/employees/me` — Current employee profile

### Family Members
- `POST   /api/v1/family/` — Add family member
- `GET    /api/v1/family/` — List my family members
- `PUT    /api/v1/family/{id}` — Update family member
- `DELETE /api/v1/family/{id}` — Remove family member

### Policies
- `GET    /api/v1/policies/` — List available policies
- `POST   /api/v1/policies/` — Create policy (admin/insurer)
- `GET    /api/v1/policies/{id}` — Policy details
- `POST   /api/v1/policies/{id}/enroll` — Employee enrolls in policy
- `GET    /api/v1/policies/my-policies` — My enrolled policies

### Health Cards
- `GET    /api/v1/health-cards/my-card` — Get my health card
- `POST   /api/v1/health-cards/generate` — Generate health card

### Claims
- `POST   /api/v1/claims/` — Initiate claim
- `GET    /api/v1/claims/` — List my claims
- `GET    /api/v1/claims/{id}` — Claim details
- `POST   /api/v1/claims/{id}/documents` — Upload documents
- `PUT    /api/v1/claims/{id}/status` — Update status (admin/insurer)
- `GET    /api/v1/claims/{id}/timeline` — Claim audit timeline

---

## 6. Database Tables

1. `users` — Auth accounts with roles
2. `employees` — Employee profiles linked to users
3. `family_members` — Dependents of employees
4. `policies` — Insurance policy definitions
5. `policy_enrollments` — Employee-to-policy mapping
6. `claims` — Insurance claims
7. `claim_documents` — Documents attached to claims
8. `claim_status_history` — Audit trail of claim status changes
9. `health_cards` — Employee health card data
10. `health_checkups` — Scheduled health checkup records
11. `lab_partners` — Partner labs for checkups
12. `tickets` — Support tickets
13. `notifications` — User notifications
14. `audit_logs` — System-wide audit trail
15. `ai_audit_logs` — AI interaction audit trail

---

## 7. AI Integration Points (Planned)

| Module | AI Feature | Priority |
|--------|-----------|---------|
| Claims | Document classification | High |
| Claims | Missing document detection | High |
| Claims | Fraud signal scoring | High |
| Claims | Auto-summary | Medium |
| Support | AI chatbot (RAG over policies) | High |
| Support | Auto-ticket categorization | Medium |
| OCR | Structured field extraction | High |
| Recommendations | Cross-sell engine | Medium |
| Health | Report summarization | Medium |

---

## 8. Security Checklist

- [x] JWT with expiry + refresh tokens
- [x] Password hashing (bcrypt)
- [x] Role-based access control (RBAC)
- [x] Audit logging on all mutations
- [x] PII masking layer for AI calls (planned)
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] CORS configured
- [x] Secrets via env vars only
- [ ] Rate limiting (Phase 2)
- [ ] AI response validation (Phase 2)
- [ ] Encryption at rest (Phase 3)
- [ ] Vector DB access control (Phase 3)

---

## 9. Important Notes

- The DB URL is set via `DATABASE_URL` env var — change to PostgreSQL without touching code
- All timestamps are UTC
- Soft deletes used throughout (is_active flag) — no hard deletes in prod
- Every API response follows a standard envelope: `{success, data, message, meta}`
- AI calls MUST go through `ai_services/` layer — never call LLM directly from routers
- PII fields: name, aadhaar, pan, phone, email, dob — always masked before AI

---

## 10. Next Steps (Phase 2)

1. React frontend — authentication flows + dashboard
2. OCR pipeline — document upload + field extraction
3. AI Claim Assistant — LangChain integration
4. Ticketing system with AI chatbot
5. Health Checkup scheduling workflow
6. Notification engine (email/push)
