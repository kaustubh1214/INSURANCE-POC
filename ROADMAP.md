# ROADMAP.md
> Sprint plan and milestone tracking for InsureBridge POC

---

## Phase 1 — Foundation (Current Sprint)
**Goal:** Working backend with auth, core modules, DB, and Docker

| Task | Status | Priority |
|------|--------|----------|
| System architecture design | ✅ Done | Critical |
| Folder structure scaffolding | ✅ Done | Critical |
| SQLAlchemy models (all 15 tables) | ✅ Done | Critical |
| Auth module (JWT + RBAC) | ✅ Done | Critical |
| User management module | ✅ Done | High |
| Employee management module | ✅ Done | High |
| Family member module | ✅ Done | High |
| Policy management module | ✅ Done | High |
| Health card module | ✅ Done | High |
| Claims management + workflow | ✅ Done | Critical |
| Docker + docker-compose | ✅ Done | High |
| Documentation (4 files) | ✅ Done | High |

---

## Phase 2 — Frontend + AI Foundation
**Goal:** Working UI + first AI features

| Task | Status | Priority |
|------|--------|----------|
| React + Vite app scaffolding | 🔲 Pending | Critical |
| Auth pages (Login/Register) | 🔲 Pending | Critical |
| Employee dashboard | 🔲 Pending | High |
| Policy view page | 🔲 Pending | High |
| Claims submission UI | 🔲 Pending | High |
| Family member management UI | 🔲 Pending | High |
| Health card UI | 🔲 Pending | Medium |
| OCR pipeline (Tesseract) | 🔲 Pending | High |
| AI Claim document classifier | 🔲 Pending | High |
| Missing document detector | 🔲 Pending | High |
| Ticket system backend | 🔲 Pending | Medium |
| Notification engine | 🔲 Pending | Medium |
| Health checkup scheduling | 🔲 Pending | Medium |

---

## Phase 3 — Advanced AI + Admin
**Goal:** Full AI features + admin dashboard

| Task | Status | Priority |
|------|--------|----------|
| RAG chatbot (LangChain + ChromaDB) | 🔲 Pending | High |
| AI fraud scoring | 🔲 Pending | High |
| AI claim auto-summary | 🔲 Pending | Medium |
| Cross-sell recommendation engine | 🔲 Pending | Medium |
| Admin dashboard (React) | 🔲 Pending | High |
| Health report AI summarizer | 🔲 Pending | Medium |
| Lab partner integration | 🔲 Pending | Medium |
| Email notification integration | 🔲 Pending | Low |

---

## Phase 4 — Production Hardening
**Goal:** Enterprise-ready, demo-ready

| Task | Status | Priority |
|------|--------|----------|
| Migrate to PostgreSQL | 🔲 Pending | High |
| Redis + Celery for async tasks | 🔲 Pending | High |
| Rate limiting | 🔲 Pending | High |
| API documentation polish | 🔲 Pending | Medium |
| CI/CD pipeline (GitHub Actions) | 🔲 Pending | Medium |
| Security audit | 🔲 Pending | High |
| Performance testing | 🔲 Pending | Medium |
| Demo data seeder | 🔲 Pending | High |

---

## Milestones

| Milestone | Target | Description |
|-----------|--------|-------------|
| M1: Backend Core | Phase 1 End | All APIs running, auth working, DB seeded |
| M2: POC Demo Ready | Phase 2 End | Full UI + basic AI features |
| M3: AI Showcase | Phase 3 End | Chatbot, OCR, fraud detection live |
| M4: Client Presentation | Phase 4 End | Polished, hardened, documented |

---

## Known Technical Debt

1. SQLite → PostgreSQL migration needed before production
2. File storage is local → needs S3/MinIO integration
3. AI API keys hardcoded in .env → need secrets manager (Vault/AWS Secrets)
4. No rate limiting implemented yet
5. Frontend state management (Zustand) not set up yet
6. No automated test coverage yet
