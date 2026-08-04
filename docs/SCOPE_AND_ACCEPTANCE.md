# Scope, User Stories & Acceptance Criteria

**Project:** AI-Powered Construction Site Intelligence Platform  
**Phase:** Phase 0 — Planning & Requirements  

---

## 1. Module Descriptions & Definitions of Done (Acceptance Criteria)

### Module 1 / 1A: Entry-Gate PPE Detection
- **Description:** Real-time computer vision inference on gate camera stream detecting workers and checking for safety helmet and reflective vest presence.
- **User Stories:**
  - *US-1:* As a worker, I want to walk through the entry gate and have my PPE automatically verified without manual paper/ID scanning.
  - *US-2:* As a supervisor, I want to receive an immediate alert when a worker passes gate screening without required PPE.
- **Acceptance Criteria (Definition of Done):**
  1. System detects persons in the gate camera feed.
  2. Crops bounding boxes around detected individuals and determines presence of `helmet` and `vest`.
  3. Automatically posts a `violation` record to `POST /violations` if either helmet or vest is missing.
  4. Stores snapshot image path, timestamp, gate ID, and missing equipment flags.
  5. Displays non-compliant entry event on the Supervisor dashboard in < 5 seconds latency.

---

### Module 2: Restricted Zone Monitoring
- **Description:** Spatial geometry detection verifying whether detected persons enter administrator-configured polygon areas.
- **User Stories:**
  - *US-3:* As a supervisor, I want to be alerted whenever an unauthorized person enters a dangerous restricted zone.
- **Acceptance Criteria (Definition of Done):**
  1. Administrators can define restricted zone boundary polygons (coordinates) via API/UI.
  2. AI pipeline calculates if the bottom-center point of a person's bounding box falls inside any defined polygon.
  3. Violations trigger an immediate alert on the dashboard with zone name, timestamp, and visual snapshot.

---

### Module 3: Equipment Tracking & Idle Time
- **Description:** Identifies heavy machinery types (excavator, bulldozer, crane, truck) and tracks active movement vs idle status over time.
- **User Stories:**
  - *US-3B:* As a site manager, I want to monitor equipment locations and track idle hours to optimize machinery usage.
- **Acceptance Criteria (Definition of Done):**
  1. Detects and tags equipment types in camera feeds.
  2. Maintains spatial tracking IDs across frames to compute displacement.
  3. Flags equipment as "idle" if movement is below threshold for > 15 minutes.
  4. Displays active vs idle equipment statistics on dashboard summary.

---

### Module 4A: Delivery Verification & Material Tracking
- **Description:** Automated vehicle counting at gate camera combined with supervisor manual delivery reporting and material inflow logging to detect potential vendor/supervisor delivery fraud.
- **User Stories:**
  - *US-4:* As an administrator, I want automatic vehicle arrival counts compared against supervisor-reported delivery counts to catch fraud.
  - *US-5:* As a supervisor, I want to log material type, quantity, and unit alongside delivery counts so there is a searchable material arrival log.
  - *US-8:* As an administrator, I want escalated discrepancy reports sent directly to me without supervisor intervention.
- **Acceptance Criteria (Definition of Done):**
  1. AI pipeline automatically increments `ai_vehicle_count` when delivery trucks cross the gate threshold.
  2. Supervisor logs delivery via `POST /deliveries` specifying `gate_id`, `manual_reported_count`, `material_type` (e.g., cement, sand, steel), `material_quantity`, and `quantity_unit`.
  3. Discrepancy service compares `ai_vehicle_count` vs `manual_reported_count`.
  4. Single mismatch records a flagged log but does NOT trigger escalation alert.
  5. 3 consecutive mismatches at the same gate automatically trigger a pattern-based fraud escalation available strictly on `GET /deliveries/discrepancies` (Admin access only).

---

### Module 6: Hazard Reporting & AI Categorization
- **Description:** Worker-submitted safety hazards with automated AI classification into standardized categories.
- **User Stories:**
  - *US-6:* As a worker, I want to upload a hazard photo with description and location so it gets categorized and routed to site supervisors.
- **Acceptance Criteria (Definition of Done):**
  1. Worker can submit form via `POST /hazard-reports` with multipart image upload, location string, and description.
  2. System enforces image validation (JPEG/PNG, max size 5MB).
  3. AI classifier automatically assigns a category (`fire_risk`, `unsafe_wiring`, `water_leakage`, `scaffold_damage`, `structural_cracks`, or `other`).
  4. Report appears on supervisor/admin hazard review feed.

---

### Module 7: Central Dashboard & Safety Intelligence
- **Description:** Unified responsive web view for real-time monitoring of site status, KPIs, and alerts.
- **User Stories:**
  - *US-7:* As an administrator, I want to view all site metrics, active violations, material inflows, and fraud alerts on one dashboard.
- **Acceptance Criteria (Definition of Done):**
  1. Displays aggregate KPI summary: daily worker count, PPE compliance rate (%), active equipment, delivery counts, open hazards.
  2. Renders live/recent violations feed with filters by date, severity, and gate.
  3. Renders material inflow charts grouped by material type.
  4. Provides role-guarded views (Admin sees fraud escalations; Supervisors see operational management; Workers see hazard submission screen).

---

## 2. Explicitly Out of Scope (NOT Built in v1)

1. **Material Inventory Forecasting / Prediction:** No predictive models forecasting future stock shortages or reorder dates.
2. **Project Progress Estimation:** No 3D reconstruction or image comparison for calculating % completion of structures.
3. **Drone / IoT Integration:** No live drone feeds, wearable IoT telemetry sensors, or RFID badge scanners.
4. **Vendor / Driver Mobile App or QR Confirmation:** No vendor-facing login, mobile app, or driver QR code check-in screens.
5. **AI Automated Cargo Inspection:** AI will NOT attempt to inspect inside closed truck containers or verify cargo material types automatically. Material attributes rely on manual supervisor logging.
6. **Native Mobile App:** Application is a web app (React + Tailwind) responsive on mobile web browsers, not a native iOS/Android binary.
