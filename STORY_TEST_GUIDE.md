# InsureBridge — Story Testing Guide
> You are **Ravi Mehta**, HR Admin at TechCorp India.
> Follow this story from start to finish to manually test every feature.

---

## Chapter 1 — Login: Enter the Platform
**URL:** `localhost:5173/login`

1. In **Email address** type: `admin@insurebridge.com`
2. In **Password** type: `Admin@123456`
3. Click **Sign in**

✅ **Expected:** You land on the Dashboard. Sidebar appears on the left with all navigation links.

---

## Chapter 2 — Dashboard: Get Your Bearings
**URL:** `localhost:5173/dashboard`

1. Look at the **4 stat cards** at the top — Total Claims, Active Policies, Family Members, Open Tickets.
   > All show 0 right now — they fill in as you complete this walkthrough.
2. Find the **Quick Actions** panel on the right — 4 shortcut buttons.
3. Notice the sidebar links: Dashboard, My Policies, Claims, Family Members, Health Card, Health Checkups, Support, Admin Panel.

---

## Chapter 3 — Family Members: Add Your Dependents
**URL:** `localhost:5173/family`

1. Click **Family Members** in the sidebar.
2. Click **+ Add Member** (top right).
3. Fill in the modal — add your spouse:
   - Full Name: `Priya Mehta`
   - Relationship: `Spouse`
   - Gender: `Female`
   - Date of Birth: `1990-06-15`
   - Aadhaar (optional): `1234 5678 9012`
4. Click **Add Member**.

✅ **Expected:** Priya's card appears in the grid.

5. Click **+ Add Member** again — add a child:
   - Full Name: `Aryan Mehta`
   - Relationship: `Child`
   - Gender: `Male`
   - Date of Birth: `2015-03-20`
6. Click **Add Member**.

✅ **Expected:** Both Priya and Aryan show as cards. Dashboard "Family Members" counter → 2.

**Bonus tests:**
- Click the **edit (pencil) icon** on Priya's card → update her phone → save.
- Click the **delete icon** → confirm → card disappears (soft delete, data is preserved in DB).

---

## Chapter 4 — Policies: Enroll in a Health Plan
**URL:** `localhost:5173/policies`

1. Click **My Policies** in the sidebar.
2. Click the **Available Plans** tab.
3. Browse the policy cards — each shows premium, sum insured, and plan type badge.
4. Click **Enroll** on any plan (e.g. a Family Floater).

✅ **Expected:** Success toast appears. Plan moves to your "My Policies" tab.

5. Click **My Policies** tab — confirm your enrollment with an Active badge.

---

## Chapter 5 — Claims: File and Track a Claim
**URL:** `localhost:5173/claims`

### 5a — File the claim
1. Click **Claims** in the sidebar.
2. Click **+ New Claim**.
3. Fill in the claim form:
   - Policy Enrollment: select your enrolled policy from the dropdown
   - Claim Type: `Hospitalization`
   - Hospital Name: `Apollo Hospital, Mumbai`
   - Diagnosis: `Acute Appendicitis`
   - Claimed Amount: `85000`
   - Date of Admission: today's date
   - Date of Discharge: tomorrow
4. Click **Submit Claim**.

✅ **Expected:** Claim appears in the table with a yellow **Submitted** badge and a claim number like `CLM-20260528-XXXXXX`.

### 5b — View the timeline
5. Click anywhere on the claim row.

✅ **Expected:** A Timeline Drawer slides in from the right showing:
- Claim details (hospital, diagnosis, claimed amount)
- Status history with timestamps
- AI Fields section (fraud score, priority score — shows 0 until Phase 3 AI is wired up)

### 5c — Filter claims
6. Click the status filter pills above the table.
7. Click **Submitted** → only your claim shows.
8. Click **All** → resets.

---

## Chapter 6 — Health Checkup: Book Your Annual Test
**URL:** `localhost:5173/checkups`

1. Click **Health Checkups** in the sidebar.
2. Read the **"How It Works"** steps shown on the page (Book → Confirm → Visit → Report).
3. Click **Book Checkup**.
4. Fill in the booking modal:
   - Checkup Type: `Annual Health Checkup`
   - Package Name: `Comprehensive Panel`
   - Preferred Date: any date next week
   - Lab Partner: select any from the dropdown
   - Home Collection: toggle **ON**
5. Click **Confirm Booking**.

✅ **Expected:** New checkup card appears with status **Booked**, preferred date, and home collection indicator.

---

## Chapter 7 — Support Ticket: Report an Issue
**URL:** `localhost:5173/tickets`

1. Click **Support** in the sidebar.
2. Click **+ New Ticket**.
3. Fill in:
   - Subject: `Claim document upload failing`
   - Category: `Claims`
   - Priority: `High`
   - Description: `When I upload a PDF for my claim, the page shows an error after 10 seconds.`
4. Click **Submit Ticket**.

✅ **Expected:** Ticket appears with a generated number `TKT-XXXXXX` and **Open** status badge.

5. Click on the ticket card to expand it — read the full description and category badge.

---

## Chapter 8 — Admin Panel: Review and Approve the Claim
**URL:** `localhost:5173/admin`

1. Click **Admin Panel** at the bottom of the sidebar (only visible to admin/hr/insurer roles).
2. See the claims table with **AI Fraud Score** and **AI Priority Score** progress bars.
   > Scores show 0 now — they populate in Phase 3 when the AI service is connected.
3. Find Ravi's claim (Apollo Hospital, ₹85,000).
4. Change the status: `Submitted` → **Under Review** → save.

✅ **Expected:** Status badge updates in the admin table.

5. Go back to **Claims** in the sidebar. Click the claim row → open Timeline Drawer.

✅ **Expected:** Timeline now shows 2 entries: "Submitted" → "Under Review" with timestamps.

6. Go back to **Admin Panel**. Change status to **Approved**, then **Settled**.
7. Check the timeline one more time — it should show **4 entries** total.

✅ **Complete end-to-end claim lifecycle tested!**

---

## Full Flow Summary

| Step | Page | What you tested |
|------|------|----------------|
| 1 | `/login` | JWT authentication |
| 2 | `/dashboard` | Stats + quick actions |
| 3 | `/family` | Add / edit / delete dependents |
| 4 | `/policies` | Browse plans + enroll |
| 5 | `/claims` | File claim + view timeline + filter |
| 6 | `/checkups` | Book annual checkup |
| 7 | `/tickets` | Raise support ticket |
| 8 | `/admin` | Review claims + full status workflow |

---

## Swagger API Explorer (Bonus)

Open **http://localhost:8000/docs** to explore all 42+ API endpoints directly.

To authenticate in Swagger:
1. Call `POST /api/v1/auth/login` with `admin@insurebridge.com` / `Admin@123456`
2. Copy the `access_token` from the response
3. Click **Authorize** (top right) → paste `Bearer <token>`
4. All protected endpoints are now unlocked
