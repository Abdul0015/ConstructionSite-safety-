# Product Requirements Document (PRD)
## AI-Powered Construction Site Intelligence Platform

**Version:** 1.1  
**Status:** Approved & Finalized  
**Owner:** Product Management & Technical Architecture  

---

## 1. Executive Summary
The AI-Powered Construction Site Intelligence Platform is an automated computer-vision-driven safety, compliance, and monitoring solution tailored for construction environments. It automates PPE compliance checks at entry points, monitors restricted hazardous zones, tracks key equipment, verifies delivery vehicle counts against manual reports to prevent fraud, logs incoming materials, and centralizes hazard reporting and site safety analytics into a single dashboard for supervisors and site administrators.

---

## 2. Problem Statement
Manual safety inspections and unstructured CCTV reviews are slow, error-prone, and reactive. Key pain points include:
- Undetected PPE violations resulting in preventable workplace injuries.
- Unenforced restricted zone perimeters.
- Untracked equipment location and idle time.
- Vendor/supervisor delivery quantity fraud.
- Unstructured, paper-based hazard reports with no audit trail or categorization.
- Absence of a centralized, real-time single source of truth for site safety.

---

## 3. Core Vision & System Goals
- **G1 (PPE Enforcement):** Prevent non-compliant workers from entering site entry points.
- **G2 (Fraud Mitigation):** Provide automated, tamper-evident vehicle delivery verification.
- **G3 (Material Auditing):** Maintain an auditable log of material inflow (type, quantity) tied to delivery events.
- **G4 (Hazard Management):** Centralize hazard submission with AI-assisted categorization.
- **G5 (Unified Oversight):** Provide real-time site KPIs, alerts, and analytics via an Admin & Supervisor dashboard.
- **G6 (Scalable Pipeline):** Establish a reusable computer vision camera processing pipeline.

---

## 4. System Actors & Roles

| Role | Access Level | Key Responsibilities |
|---|---|---|
| **Administrator** | Full System Access | Multi-site oversight, user management, resolving flagged delivery fraud escalations, defining restricted zones. |
| **Supervisor** | Site Operational Access | Daily compliance monitoring, acknowledging alerts, submitting manual delivery logs with material info. |
| **Worker** | Limited Submission Access | Undergoes PPE entry gate screening, submits hazard reports with photos/descriptions. |
| *(Passive)* **Vendor / Driver** | No Direct App Access | Passive subjects; vehicles are detected automatically by gate cameras. |

---

## 5. Core System Modules (In Scope)

1. **Module 1 / 1A — Entry-Gate PPE Detection:** Detects helmets and safety vests on incoming workers via gate camera streams, creating violation audit entries for non-compliance.
2. **Module 2 — Restricted Zone Monitoring:** Performs polygon-based spatial intersection checks on detected persons in restricted site areas and fires real-time supervisor alerts.
3. **Module 3 — Equipment Tracking & Idle Time:** Classifies machinery types, tracks spatial location, and calculates operational vs. idle durations.
4. **Module 4A — Delivery Verification & Material Inflow:** Automates gate delivery vehicle counts, accepts supervisor manual delivery/material entries, and detects repeated count discrepancies for fraud escalation.
5. **Module 6 — Hazard Reporting & AI Categorization:** Captures worker hazard submissions and automatically classifies hazard types (fire risk, electrical, structural, scaffolding, water).
6. **Module 7 — Central Safety & Intelligence Dashboard:** Displays aggregated real-time site analytics, compliance rates, active alerts, delivery discrepancies, and material logs.

---

## 6. Business Rules & Fraud Mitigation Logic
1. **Discrepancy Escalation Routing:** Delivery count mismatches (AI detected count vs. Supervisor reported count) are routed strictly to Administrators to avoid conflict of interest.
2. **Pattern-Based Escalation:** A single count mismatch does NOT trigger a fraud alert. Only repeated/patterned discrepancies (e.g., 3 consecutive mismatches) escalate to the Administrator.
3. **Material Data Input:** Cargo contents and exact material quantities are manually entered by the Supervisor. AI verifies vehicle arrival count and vehicle type classification.
4. **Audit Trail Immutability:** Violations and delivery log entries are append-only records with no update or delete APIs exposed.
