# START HERE — InsureBridge Platform
> **Read this first.** Everything you need to run, test, and demo the platform is in this single file.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Environment Setup](#2-environment-setup)
3. [Option A — Run Without Docker (Recommended for Dev)](#3-option-a--run-without-docker)
4. [Option B — Run With Docker](#4-option-b--run-with-docker)
5. [Verify Everything Is Running](#5-verify-everything-is-running)
6. [Demo Credentials](#6-demo-credentials)
7. [UI Testing — Step-by-Step Walkthrough](#7-ui-testing--step-by-step-walkthrough)
8. [API Documentation](#8-api-documentation)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### Without Docker
| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ (20 recommended) | `node --version` |
| npm | 9+ | `npm --version` |

### With Docker
| Tool | Minimum Version | Check |
|------|----------------|-------|
| Docker Desktop | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |

---

## 2. Environment Setup

### Copy the environment file
```bash
cd "D:\insurance poc\backend"
copy .env.example .env
```

### Edit `.env` — minimum required changes
Open `backend\.env` in any text editor and set:
```env
# REQUIRED — change this in production, fine to leave for POC
JWT_SECRET_KEY=insurebridge-super-secret-key-change-in-prod-2024

# Database — SQLite, zero config needed for POC
DATABASE_URL=sqlite+aiosqlite:///./insurebridge.db

# Admin user auto-created on first run
ADMIN_EMAIL=admin@insurebridge.com
ADMIN_PASSWORD=Admin@123456
ADMIN_NAME=Super Admin

# Optional — only needed for real AI features (Phase 3)
# OPENAI_API_KEY=sk-...
```

> Everything else in `.env.example` has safe defaults. You only need the above to run the POC.

---

## 3. Option A — Run Without Docker

Open **two terminal windows** side by side.

### Terminal 1 — Backend (FastAPI)

```bash
# Navigate to backend
cd "D:\insurance poc\backend"

# Create Python virtual environment
python -m venv venv

# Activate (Windows Command Prompt)
venv\Scripts\activate

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     InsureBridge starting up...
INFO:     Database initialized
INFO:     Admin user seeded: admin@insurebridge.com
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Terminal 2 — Frontend (React + Vite)

```bash
# Navigate to frontend
cd "D:\insurance poc\frontend"

# Install Node dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in 800ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### ✅ App is ready at: http://localhost:5173

---

## 4. Option B — Run With Docker

```bash
# Navigate to project root
cd "D:\insurance poc"

# Build and start all services
docker compose up --build

# To run in background (detached)
docker compose up --build -d

# To stop
docker compose down

# To stop and delete the database volume (fresh start)
docker compose down -v
```

**Expected output:**
```
[+] Building backend ...
[+] Building frontend ...
[+] Running 2/2
 ✔ Container insurebridge-backend   Started
 ✔ Container insurebridge-frontend  Started
```

### ✅ App is ready at: http://localhost:3000 (Docker)
### ✅ Backend API at: http://localhost:8000 (Docker)

---

## 5. Verify Everything Is Running

Open your browser and check these URLs:

| URL | Expected Result |
|-----|----------------|
| http://localhost:5173 | Redirects to /login page |
| http://localhost:8000/health | `{"status": "healthy", ...}` JSON |
| http://localhost:8000/docs | Swagger API documentation |
| http://localhost:8000/redoc | ReDoc API documentation |

If you see the login page — **you're ready to test!**

---

## 6. Demo Credentials

These users are available for testing different role experiences:

| Role | Email | Password | Access |
|------|-------|----------|--------|
| **Admin** | admin@insurebridge.com | Admin@123456 | Everything, including Admin panel |
| **Employee** | Register a new account | Any (8+ chars, 1 number, 1 special) | Employee portal |

> **Tip:** Register a new account using `POST /api/v1/auth/register` via Swagger UI (http://localhost:8000/docs) to test the employee role separately. Or just use the Admin account for the full demo.

---

## 7. UI Testing — Step-by-Step Walkthrough

### 🔐 Step 1 — Login

1. Open http://localhost:5173
2. You will be automatically redirected to `/login`
3. Enter credentials:
   - **Email:** `admin@insurebridge.com`
   - **Password:** `Admin@123456`
4. Click **Sign In**
5. **Expected:** Redirected to `/dashboard` with a greeting like "Good morning, Super Admin"

---

### 📊 Step 2 — Dashboard

**URL:** `/dashboard`

What to verify:
- [ ] 4 stat cards visible (Total Claims, Active Policies, Family Members, Open Tickets)
- [ ] "Recent Claims" table shows (empty for fresh run — that's normal)
- [ ] "Quick Actions" buttons on the right: File a Claim, View Health Card, Book Checkup, New Ticket
- [ ] "Active Policies" section on the right
- [ ] Sidebar is visible with all navigation links
- [ ] Top header shows notification bell and user avatar

> **Note:** Stats will show 0/empty on a fresh database. They populate as you create data in subsequent steps.

---

### 👨‍👩‍👧 Step 3 — Add Family Members

**URL:** `/family` (click "Family" in sidebar)

1. Click **"+ Add Member"** button (top right)
2. Fill in the modal:
   - Full Name: `Priya Sharma`
   - Relationship: `Spouse`
   - Date of Birth: any past date
   - Gender: `Female`
   - Aadhaar (optional): `1234-5678-9012`
3. Click **Save Member**
4. **Expected:** New card appears in the grid with the member's name and relationship icon

Repeat for a child:
- Full Name: `Rahul Sharma`
- Relationship: `Child`

**Verify:**
- [ ] Both members appear as cards
- [ ] Edit button (pencil icon) opens edit modal
- [ ] Delete button soft-deletes (card disappears, data preserved in DB)

---

### 📋 Step 4 — Browse Available Policies

**URL:** `/policies` (click "Policies" in sidebar)

1. You'll see two tabs: **"My Policies"** and **"Available Plans"**
2. Click **"Available Plans"** tab
3. **Expected:** Policy cards showing plan names, premium, sum insured, and type badges
4. Click **"Enroll"** on any policy
5. **Expected:** Success message + policy moves to "My Policies" tab
6. Click **"My Policies"** tab to verify enrollment

> **Tip:** Create more policies via Swagger (POST /api/v1/policies/) using the admin JWT token for a richer demo.

---

### 🏥 Step 5 — File a New Claim

**URL:** `/claims` (click "Claims" in sidebar)

**5a. Create a claim:**
1. Click **"+ New Claim"** button
2. Fill in the modal:
   - Select Policy Enrollment (dropdown)
   - Claim Type: `Hospitalization`
   - Hospital Name: `Apollo Hospital, Mumbai`
   - Diagnosis: `Acute Appendicitis`
   - Claimed Amount: `85000`
   - Date of Admission: any recent date
   - Date of Discharge: day after admission
3. Click **Submit Claim**
4. **Expected:** Claim appears in the table with status badge **"Submitted"**

**5b. View claim timeline:**
1. Click on any claim row in the table
2. A **Timeline Drawer** slides in from the right
3. **Expected:**
   - Full claim details (hospital, diagnosis, amount)
   - Status history timeline showing "Submitted" event
   - AI Fields section (fraud score, priority score — will show 0 until Phase 3 AI is enabled)

**5c. Filter claims by status:**
1. Click the status filter pills above the table (All, Submitted, Under Review, etc.)
2. **Expected:** Table filters to show only claims with that status

---

### 💳 Step 6 — Health Card

**URL:** `/health-card` (click "Health Card" in sidebar)

**First, generate a health card (Admin step via API):**
1. Open http://localhost:8000/docs
2. Authorize: click the **"Authorize"** button → enter Bearer token
   - Get token from: Login response or use the `/auth/login` endpoint in Swagger
3. Find `POST /api/v1/health-cards/generate`
4. Execute with body:
   ```json
   {
     "employee_id": "<your_employee_id>",
     "insurer_name": "Star Health Insurance",
     "valid_from": "2024-01-01",
     "valid_to": "2025-12-31",
     "sum_insured": 500000,
     "tpa_name": "Medi Assist",
     "tpa_helpline": "1800-425-9090"
   }
   ```

**Then view in UI:**
1. Go back to the frontend at `/health-card`
2. **Expected:**
   - Gradient health card visual with card number
   - Validity countdown (days remaining)
   - TPA helpline details
   - "Print / Save PDF" hint

> **Note:** If you see "No health card found", you need to first create an Employee profile linked to your user (via Swagger POST /api/v1/employees/) and then generate the card.

---

### 🔬 Step 7 — Book Health Checkup

**URL:** `/checkups` (click "Checkups" in sidebar)

1. Click **"Book Checkup"** button
2. The modal opens with:
   - Checkup Type dropdown
   - Package Name
   - Preferred Date (calendar picker)
   - Lab Partner selector (loads from API)
   - Home Collection toggle
3. Select any options and click **"Confirm Booking"**
4. **Expected:**
   - New checkup card appears with status **"Booked"**
   - Card shows package name, preferred date, home collection indicator

**Verify the "How It Works" section:**
- [ ] 4 steps visible below the page header (Book → Confirm → Visit → Report)

---

### 🎫 Step 8 — Support Tickets

**URL:** `/tickets` (click "Tickets" in sidebar)

**8a. Create a ticket:**
1. Click **"+ New Ticket"** button
2. Fill in the modal:
   - Subject: `Unable to download claim documents`
   - Category: `Claims`
   - Priority: `High`
   - Description: `When I try to download my claim document for CLM-XXXX, the page shows an error.`
3. Click **Submit Ticket**
4. **Expected:** Ticket appears with a generated number like `TKT-202405121345-A1B2`

**8b. View ticket details:**
1. Click on any ticket card to expand it
2. **Expected:**
   - Full description
   - Category and priority badges
   - Status indicator (Open / In Progress / Resolved)
   - AI Resolution Suggestion (populated after admin action)

---

### 👑 Step 9 — Admin Panel

**URL:** `/admin` (only visible for admin/hr/insurer roles)

1. Click **"Admin"** in the sidebar (appears under the separator line for admin users)
2. **Expected:**
   - Alert banners for pending/urgent items
   - Summary stat cards (All Claims, Pending Review, High Risk, Approved Today)
   - Claims table with:
     - **AI Fraud Score** — color-coded progress bars (green=low, yellow=medium, red=high)
     - **AI Priority Score** — similar progress bars
     - Action buttons to update claim status

**9a. Update a claim status:**
1. Find a claim in the admin table
2. Click the **status dropdown** or action button
3. Change from `Submitted` → `Under Review`
4. **Expected:** Status updates in the table; claim timeline gains a new entry

---

### 🔄 Step 10 — Full Claim Workflow Test

This tests the complete claim state machine end-to-end:

1. **Employee files claim** → Status: `Submitted`
2. **Admin reviews** → Change to `Under Review`
3. **Admin requests documents** → Change to `Pending Documents`
4. **Employee uploads document** → via `/claims/{id}/documents` in Swagger
5. **Admin approves** → Change to `Approved`
6. **Admin settles** → Change to `Settled`

Verify each step shows in the timeline drawer on the `/claims` page.

---

## 8. API Documentation

### Swagger UI (Interactive)
**http://localhost:8000/docs**

How to authenticate in Swagger:
1. Expand `POST /api/v1/auth/login`
2. Click **"Try it out"**
3. Enter: `{"email": "admin@insurebridge.com", "password": "Admin@123456"}`
4. Execute — copy the `access_token` from response
5. Click **"Authorize"** button at the top of the page
6. Enter: `Bearer <paste_your_token_here>`
7. Now all authenticated endpoints are unlocked

### ReDoc (Read-only docs)
**http://localhost:8000/redoc**

### Full API Endpoint Reference

| Module | Count | Base Path |
|--------|-------|-----------|
| Auth | 5 | `/api/v1/auth/` |
| Users | 4 | `/api/v1/users/` |
| Employees | 5 | `/api/v1/employees/` |
| Family Members | 4 | `/api/v1/family/` |
| Policies | 5 | `/api/v1/policies/` |
| Claims | 8 | `/api/v1/claims/` |
| Health Cards | 2 | `/api/v1/health-cards/` |
| Health Checkups | 3 | `/api/v1/health-checkups/` |
| Support Tickets | 4 | `/api/v1/tickets/` |
| **Total** | **40+** | |

---

## 9. Troubleshooting

### Backend won't start — `ModuleNotFoundError`
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
# Then reinstall
pip install -r requirements.txt
```

### Backend won't start — `aiosqlite` not found
```bash
pip install aiosqlite
```

### Frontend won't start — `node_modules not found`
```bash
cd "D:\insurance poc\frontend"
npm install
```

### Frontend shows blank page / white screen
```bash
# Check browser console (F12) for errors
# Most common cause: backend not running
# Verify backend is up: http://localhost:8000/health
```

### Login fails with "Invalid credentials"
```bash
# Delete the database and restart backend (re-seeds admin user)
cd "D:\insurance poc\backend"
del insurebridge.db   # Windows
rm insurebridge.db    # Mac/Linux
# Then restart uvicorn
```

### CORS error in browser console
- Make sure backend is running on port **8000** (not any other port)
- Make sure frontend is running on port **5173** (Vite default)
- If using a different port, update `CORS_ORIGINS` in `backend/.env`

### PowerShell execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker: port already in use
```bash
# Find what's using the port
netstat -ano | findstr :8000
# Kill that process, then retry docker compose up
```

### Docker: fresh database (wipe everything)
```bash
docker compose down -v
docker compose up --build
```

---

## 10. Project Structure (Quick Reference)

```
insurance poc/
├── START_HERE.md          ← You are here
├── PROJECT_CONTEXT.md     ← Living architecture doc
├── DEVELOPMENT_LOG.md     ← Change history
├── SYSTEM_ARCHITECTURE.md ← Full technical diagrams
├── ROADMAP.md             ← Phase plan
├── docker-compose.yml
│
├── backend/
│   ├── .env               ← Your config (copy from .env.example)
│   ├── .env.example       ← Template
│   ├── requirements.txt
│   └── app/
│       ├── main.py        ← FastAPI entry point
│       ├── config.py      ← Settings
│       ├── database.py    ← SQLAlchemy async engine
│       ├── core/          ← Security, RBAC, exceptions, response
│       ├── modules/       ← auth, users, employees, family, policies,
│       │                     claims, health_cards, health_checkups, tickets
│       └── ai_services/   ← PII masker, claim AI, OCR stubs
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx         ← Router + route guards
        ├── services/       ← api.ts (axios), authService.ts
        ├── store/          ← Zustand auth store
        ├── types/          ← TypeScript interfaces
        └── pages/
            ├── auth/       ← LoginPage
            ├── dashboard/  ← DashboardPage
            ├── policies/   ← PoliciesPage
            ├── claims/     ← ClaimsPage
            ├── family/     ← FamilyPage
            ├── health/     ← HealthCardPage, HealthCheckupsPage
            ├── tickets/    ← TicketsPage
            └── admin/      ← AdminPage
```

---

> **Phase 3 (Next):** AI Claim Assistant, OCR Document Pipeline, RAG Support Chatbot, Notification Engine. See `ROADMAP.md` for the full plan.
