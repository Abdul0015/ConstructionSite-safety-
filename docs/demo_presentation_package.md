# Classroom Demo Presentation Package & Script

This package contains the exact media clips, presentation script, and local execution confirmation for demonstrating the **AI-Powered Site Intelligence Platform**.

---

## 1. Video Clips Specification & Sources

All video clips are stored in `storage/demo_clips/` for offline local presentation without requiring internet access:

| Clip ID | File Name | Clip Content & Description | Expected Model Detection / System Response |
| :--- | :--- | :--- | :--- |
| **Clip 1** | `demo_no_helmet.mp4` | Worker walking near gate without a safety hardhat. | Detects person, crops bbox, classifies `helmet_missing=True`, triggers HTTP `POST /violations/internal`, creates `Violation` row & `GateEntry` row (`passed_ppe=False`). |
| **Clip 2** | `demo_compliant.mp4` | Worker walking near gate wearing full hardhat and high-vis vest. | Detects person, classifies `passed_ppe=True`, logs `GateEntry` (`passed_ppe=True`). Zero violation rows created. |
| **Clip 3** | `demo_vehicle_entry.mp4` | Flatbed delivery truck crossing gate camera ROI line at `y=300`. | Gate vehicle tracking counter detects centroid crossing line, increments `ai_vehicle_count` from `0` to `1`. |
| **Clip 4** | `demo_restricted_zone.mp4` | Person stepping inside polygon coordinates `[[10, 10], [300, 10], [300, 300], [10, 300]]`. | Ray-casting point-in-polygon check evaluates ground point `((x1+x2)/2, y2)` inside polygon → logs `restricted_zone_entry` violation. |
| **Clip 5** | `demo_low_light_limitation.mp4` | Heavy night-time shadow / heavy camera occlusion clip. | **Honest Limitation Demonstration:** Model confidence drops below `0.5` threshold or fails due to lack of infrared lighting, demonstrating transparent engineering limitations. |

---

## 2. Step-by-Step Presentation Script (Ordered Presentation Flow)

1. **Step 1 — Initial Baseline (Empty Dashboard State):**
   - Open Central Dashboard. Demonstrate `worker_count = 0`, `ppe_compliance_rate = None` (Insufficient Data), `total_delivery_count = 0`.
2. **Step 2 — Trigger Safety Violation (`demo_no_helmet.mp4`):**
   - Play Clip 1. Point out the live terminal detection logs and show the dashboard updating compliance rate to reflect the non-compliant entry.
3. **Step 3 — Trigger Compliant Gate Entry (`demo_compliant.mp4`):**
   - Play Clip 2. Show `GateEntry` row logged with `passed_ppe = True`. Point out how `ppe_compliance_rate` dynamically adjusts based strictly on real DB audit rows.
4. **Step 4 — Gate Vehicle Counter (`demo_vehicle_entry.mp4`):**
   - Play Clip 3. Demonstrate truck crossing ROI line `y=300`. Show AI tracking counter registering `ai_vehicle_count = 1`.
5. **Step 5 — Supervisor Delivery Log & Discrepancy Flagging:**
   - Log in as Supervisor. Manually submit delivery count = `2` (mismatch vs AI count `1`). Show `discrepancy_flag = True` on the delivery log.
6. **Step 6 — Worker Hazard Report Submission & AI Categorization:**
   - Log in as Worker. Submit hazard description `"Exposed electrical wires sparking near puddle"`. Show AI auto-categorizing report as `"electrical"`.
7. **Step 7 — Admin Discrepancy Escalation Screen:**
   - Submit 2 more mismatched delivery logs at the same gate (reaching 3 consecutive mismatches). Log in as Admin and open Escalations screen to show the `AdminNotification` alert (`severity="critical"`).
8. **Step 8 — Honest Limitation Demonstration (`demo_low_light_limitation.mp4`):**
   - Play Clip 5. Explain to the audience how dark lighting / heavy occlusions drop confidence below `0.5`, demonstrating real AI model constraints and engineering transparency.

---

## 3. Local Execution Confirmation (Docker & Zero Cloud Dependency)

- **Zero Cloud/Internet Dependency:** All pre-trained YOLOv8 weights (`yolov8n.pt`), OpenCV video processors, PostgreSQL database containers, and React frontend static bundles run 100% locally.
- **Local Spin-up Command:**
  ```bash
  docker-compose up --build
  ```
