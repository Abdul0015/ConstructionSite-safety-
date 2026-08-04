# Official Dataset & Model Training Documentation

This document serves as the official Dataset & Training reference for the **AI-Powered Construction Site Intelligence Platform**. It documents verified public dataset sources, local directory structures, class mappings, and dataset discrepancies.

---

## 1. Primary PPE Detection Dataset: Ultralytics Construction-PPE

The primary dataset used for fine-tuning the 2-stage detect-then-classify PPE detection engine is the official **Ultralytics Construction-PPE Dataset**.

- **Official Source URL:** [https://docs.ultralytics.com/datasets/detect/construction-ppe/](https://docs.ultralytics.com/datasets/detect/construction-ppe/)
- **Total Local Images:** **1,416 images**
- **Split Distribution:**
  - `images/train`: 1,132 images
  - `images/val`: 143 images
  - `images/test`: 141 images
- **Format:** YOLO standard annotation format (`.txt` per image with normalized `class_id x_center y_center width height`).

---

## 2. Official YAML Class Taxonomy

Extracted directly from the verified local `construction-ppe.yaml` configuration file:

```yaml
# Total Classes: 11
names:
  0: helmet
  1: gloves
  2: vest
  3: boots
  4: goggles
  5: none
  6: Person
  7: no_helmet
  8: no_goggle
  9: no_gloves
  10: no_boots
```

### Class Roles in Pipeline Logic:
- **Positive Compliance Classes (0–4):** `helmet`, `gloves`, `vest`, `boots`, `goggles`.
- **Explicit Violation Classes (7–10):** `no_helmet`, `no_goggle`, `no_gloves`, `no_boots`.
- **Subject Anchor Class (6):** `Person` (used to crop bounding box for PPE presence classification).
- **Background / Unclassified (5):** `none`.

---

## 3. Discrepancy Investigation & Orphaned File Resolution

During physical local disk inspection, a 10-file mismatch was detected between the image count (`1,132`) and label file count (`1,142`) in the training split.

### Root Cause Analysis:
A file-by-file stem diff between `images/train/` and `labels/train/` identified **10 orphaned duplicate label files** created with a `(1)` filename suffix during the dataset maintainer's export process:

1. `image940(1).txt`
2. `image941(1).txt`
3. `image944(1).txt`
4. `image945(1).txt`
5. `image946(1).txt`
6. `image947(1).txt`
7. `image948(1).txt`
8. `image949(1).txt`
9. `image95(1).txt`
10. `image950(1).txt`

### Impact & Safety Confirmation:
- **Image Integrity:** Every single one of the 1,132 training images in `images/train` has a valid, non-orphaned matching label file (e.g. `image940.jpg` maps directly to `image940.txt`).
- **Data Loader Behavior:** Standard YOLO / Ultralytics data loaders map label files by substituting the image path extension (`.jpg` -> `.txt`). The 10 orphaned `(1)` label files are cleanly ignored during model training and produce zero data contamination.

---

## 4. Complete System Dataset Reference Matrix

| Module | Task | Dataset Used / Source | Size / Split | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1 & 1A** | PPE Compliance & Entry-Point Verification | **Ultralytics Construction-PPE Dataset** | 1,416 images (1,132 train / 143 val / 141 test) | Fine-tuned 11-class model for helmet, vest, and violation detection. |
| **Module 1 (Auxiliary)** | General Helmet Detection | **SHWD (Safety Helmet Wearing Dataset)** | ~7,000 images (`github.com/njvisionpower`) | Optional secondary pre-training dataset for helmet-only detection. |
| **Module 2** | Zone Monitoring | Pre-trained **COCO Dataset** (`yolov8n.pt`) | 80 COCO classes | COCO `person` class used directly. Polygon intersection geometry evaluated in OpenCV/Python. |
| **Module 3 & 4A** | Vehicle Counting & Equipment Tracking | Pre-trained **COCO Dataset** (`yolov8n.pt`) | 80 COCO classes | COCO `bus`, `truck`, and `car` classes used out-of-the-box for ROI line-crossing counters. |

---

## 5. Summary & Viva Defense Note

- **Dataset Provenance:** All training resources and URLs are verified live.
- **Evaluation Rule:** Evaluation metrics (Precision, Recall, mAP@50) reported in final project documentation are calculated strictly from local validation runs on the `val` split (143 images).
