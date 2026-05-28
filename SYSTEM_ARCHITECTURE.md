# SYSTEM_ARCHITECTURE.md
> Complete technical architecture for InsureBridge Platform

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐    │
│  │  Employee Portal     │    │  Insurance Portal / Admin        │    │
│  │  React + Vite + TS  │    │  React + Vite + TS               │    │
│  └──────────┬──────────┘    └──────────────┬───────────────────┘    │
└─────────────┼─────────────────────────────┼────────────────────────┘
              │ HTTPS / REST                 │ HTTPS / REST
              ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                             │
│              FastAPI Application (Python 3.11+)                      │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│   │   Auth   │ │  CORS    │ │  Rate    │ │  Audit   │             │
│   │Middleware│ │Middleware│ │ Limiter  │ │  Logger  │             │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                            │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │  Auth    │ │Employee  │ │ Policy   │ │ Claims   │ │ Tickets │ │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │ Service │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ Health   │ │  Health  │ │ Notif.   │ │ Recommend│             │
│  │  Card    │ │ Checkup  │ │ Engine   │ │  Engine  │             │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
└─────────────────────────────────────────────────────────────────────┘
              │                             │
              ▼                             ▼
┌──────────────────────────┐  ┌───────────────────────────────────────┐
│     DATA LAYER           │  │         AI SERVICES LAYER              │
│                          │  │                                        │
│  SQLite (dev)            │  │  ┌──────────┐  ┌──────────────────┐  │
│  PostgreSQL (prod)       │  │  │  Claim   │  │  OCR Pipeline    │  │
│  SQLAlchemy ORM          │  │  │   AI     │  │  (Tesseract)     │  │
│  Alembic Migrations      │  │  └──────────┘  └──────────────────┘  │
│                          │  │  ┌──────────┐  ┌──────────────────┐  │
│  Vector Store:           │  │  │ RAG Bot  │  │  Recommendation  │  │
│  ChromaDB (dev)          │  │  │(LangChain│  │     Engine       │  │
│  Pinecone (prod)         │  │  └──────────┘  └──────────────────┘  │
└──────────────────────────┘  └───────────────────────────────────────┘
```

---

## 2. Folder Structure

```
insurebridge/
├── backend/                        # FastAPI Application
│   ├── app/
│   │   ├── main.py                 # App entry point, middleware registration
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── database.py             # SQLAlchemy engine + session factory
│   │   ├── dependencies.py         # Shared FastAPI dependencies
│   │   │
│   │   ├── core/                   # Cross-cutting concerns
│   │   │   ├── security.py         # JWT, password hashing
│   │   │   ├── rbac.py             # Role-based access control decorators
│   │   │   ├── audit.py            # Audit log writer
│   │   │   ├── exceptions.py       # Custom exception classes
│   │   │   ├── response.py         # Standard API response envelope
│   │   │   └── middleware.py       # Request logging, PII scrubbing
│   │   │
│   │   ├── modules/                # Domain modules
│   │   │   ├── auth/
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── schemas.py
│   │   │   ├── users/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── service.py
│   │   │   │   └── router.py
│   │   │   ├── employees/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── service.py
│   │   │   │   └── router.py
│   │   │   ├── family/
│   │   │   ├── policies/
│   │   │   ├── claims/
│   │   │   ├── health_cards/
│   │   │   ├── health_checkups/
│   │   │   ├── tickets/
│   │   │   ├── notifications/
│   │   │   └── admin/
│   │   │
│   │   ├── ai_services/            # All AI logic (isolated)
│   │   │   ├── base.py             # Base AI service class
│   │   │   ├── pii_masker.py       # PII detection + masking
│   │   │   ├── claim_ai/
│   │   │   │   ├── classifier.py   # Claim document classification
│   │   │   │   ├── fraud_detector.py
│   │   │   │   ├── summarizer.py
│   │   │   │   └── missing_docs.py
│   │   │   ├── ocr/
│   │   │   │   ├── extractor.py
│   │   │   │   └── doc_classifier.py
│   │   │   ├── chatbot/
│   │   │   │   ├── rag_engine.py   # RAG over policy docs
│   │   │   │   └── intent_router.py
│   │   │   └── recommendations/
│   │   │       └── cross_sell.py
│   │   │
│   │   └── models/                 # Shared SQLAlchemy base models
│   │       └── base.py
│   │
│   ├── alembic/                    # DB migrations
│   ├── tests/                      # pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                       # React + Vite + TS
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── router/                 # React Router config
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── policies/
│   │   │   ├── claims/
│   │   │   ├── family/
│   │   │   ├── health/
│   │   │   └── admin/
│   │   ├── components/             # Shared UI components
│   │   │   ├── ui/                 # shadcn/ui base components
│   │   │   ├── layout/
│   │   │   └── forms/
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── store/                  # Zustand state management
│   │   ├── services/               # API client (axios)
│   │   ├── types/                  # TypeScript interfaces
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── docker-compose.yml              # Full stack orchestration
├── docker-compose.dev.yml          # Dev overrides
├── .env.example                    # Environment variable template
├── PROJECT_CONTEXT.md
├── SYSTEM_ARCHITECTURE.md
├── DEVELOPMENT_LOG.md
└── ROADMAP.md
```

---

## 3. Database Schema (Entity Relationship)

```
users (1) ──────── (1) employees
  │                       │
  │                (many) family_members
  │                       │
  │                (many) policy_enrollments ── (many) policies
  │                       │
  │                (many) claims ──── (many) claim_documents
  │                       │               └── (many) claim_status_history
  │
  │ (1-to-1)     health_cards
  │
  └── (many) tickets
  └── (many) notifications
  └── (many) audit_logs

health_checkups ──── lab_partners
ai_audit_logs (standalone — records every LLM call)
```

---

## 4. Authentication & Authorization Flow

```
Client                  FastAPI                    Database
  │                       │                           │
  │── POST /auth/login ──►│                           │
  │                       │── Fetch user by email ──►│
  │                       │◄── user record ───────────│
  │                       │                           │
  │                       │── Verify bcrypt hash      │
  │                       │── Generate JWT (access + refresh)
  │                       │── Store refresh token ───►│
  │◄── {access_token} ────│                           │
  │                       │                           │
  │── GET /protected ─────│ (Authorization: Bearer)   │
  │  + JWT header         │── Decode JWT              │
  │                       │── Check role claims       │
  │                       │── Inject current_user     │
  │◄── Protected data ────│                           │
```

### JWT Payload Structure
```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "role": "employee",
  "employee_id": "emp_uuid",
  "iat": 1234567890,
  "exp": 1234567890
}
```

### Roles
| Role | Access Level |
|------|-------------|
| `admin` | Full system access |
| `hr` | Employee management, policy enrollment |
| `employee` | Own data, claims, health card |
| `insurer` | Policy management, claim processing |
| `agent` | Cross-sell, customer view |

---

## 5. Claim Intimation Workflow

```
Employee                 System                    Insurer/Admin
    │                      │                            │
    │── Initiate Claim ───►│                            │
    │                      │ Create claim (DRAFT)       │
    │── Upload Docs ───────►│                            │
    │                      │ OCR: Extract fields        │
    │                      │ AI: Classify documents     │
    │                      │ AI: Detect missing docs    │
    │                      │── Notify employee if missing
    │                      │                            │
    │                      │ Change status: SUBMITTED   │
    │                      │ AI: Fraud score            │
    │                      │ AI: Priority score         │
    │                      │── Route to insurer ───────►│
    │                      │                            │── Review
    │                      │◄── Status update ──────────│
    │◄── Notification ─────│                            │
    │                      │ Status: APPROVED/REJECTED  │
    │                      │ Settlement workflow        │
```

### Claim Status State Machine
```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED → SETTLED
                                 ↘ REJECTED
                  ↗ PENDING_DOCS (bounce back)
```

---

## 6. AI Services Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI SERVICES LAYER                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PII Masker (FIRST)                    │   │
│  │  Masks: name, aadhaar, pan, phone, email, dob, address   │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐ │
│  │  Claim AI    │  │   RAG Bot     │  │  OCR Pipeline        │ │
│  │              │  │               │  │                      │ │
│  │ - Classify   │  │ LangChain +   │  │ Tesseract →          │ │
│  │ - Summarize  │  │ ChromaDB      │  │ Field Extraction →   │ │
│  │ - Fraud Scan │  │ Policy Docs   │  │ Form Auto-fill       │ │
│  │ - Missing    │  │               │  │                      │ │
│  └──────────────┘  └───────────────┘  └──────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │                    AI Audit Logger                        │  │
│  │  Logs: prompt_hash, model, tokens, latency, masked_input  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. OCR Pipeline

```
Document Upload
      │
      ▼
┌─────────────┐    ┌──────────────┐    ┌───────────────────┐
│  File Store  │───►│ Doc Classifier│───►│  OCR Extractor    │
│  (local/S3) │    │ (type detect) │    │  (Tesseract)      │
└─────────────┘    └──────────────┘    └─────────┬─────────┘
                                                  │
                         ┌────────────────────────┤
                         ▼                        ▼
                  ┌──────────────┐      ┌──────────────────┐
                  │ Aadhaar OCR  │      │  Medical Bill OCR │
                  │ - Name       │      │  - Hospital       │
                  │ - DOB        │      │  - Amount         │
                  │ - Aadhaar No │      │  - Date           │
                  │ - Address    │      │  - Diagnosis      │
                  └──────────────┘      └──────────────────┘
                         │
                         ▼
                  ┌──────────────────────────┐
                  │  Field Validator          │
                  │  - Missing field check    │
                  │  - Format validation      │
                  │  - Auto-populate forms    │
                  └──────────────────────────┘
```

---

## 8. API Response Envelope

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "meta": {
    "page": 1,
    "total": 100,
    "request_id": "uuid"
  }
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "message": "Detailed error description",
  "error_code": "CLAIM_NOT_FOUND",
  "meta": { "request_id": "uuid" }
}
```

---

## 9. Security Architecture

### Layers of Defense
1. **Network**: HTTPS only, CORS whitelist
2. **Auth**: JWT validation on every protected route
3. **Authorization**: RBAC role checks
4. **Input**: Pydantic validation + SQL injection prevention
5. **AI**: PII masking before every LLM call
6. **Audit**: Immutable audit log for all state changes
7. **Data**: Soft deletes, no hard data removal

### PII Fields (Always Masked)
- Full name → `[NAME_REDACTED]`
- Aadhaar number → `XXXX-XXXX-XXXX`
- PAN → `XXXXX####X`
- Phone → `+91XXXXXXX[last4]`
- Email → `[EMAIL_REDACTED]`
- Date of birth → `[DOB_REDACTED]`
- Address → `[ADDRESS_REDACTED]`

---

## 10. Docker Architecture

```
docker-compose.yml
│
├── backend (FastAPI)
│   ├── Port: 8000
│   ├── Volume: ./backend:/app
│   └── Env: DATABASE_URL, JWT_SECRET, ...
│
├── frontend (React + Vite)
│   ├── Port: 3000
│   ├── Volume: ./frontend:/app
│   └── Env: VITE_API_URL
│
└── (Phase 2) ai_worker (Celery + Redis)
    ├── Shares backend code
    └── Handles async AI tasks
```
