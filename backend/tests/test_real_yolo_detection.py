import os
import cv2
import numpy as np
import urllib.request
import pytest
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

def download_sample_real_image(save_path: str):
    """
    Downloads a sample input image with visible persons for real un-mocked YOLOv8 model inference.
    """
    url = "https://ultralytics.com/images/bus.jpg"
    print(f"[Real Model Test] Fetching sample input image from {url}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
        out_file.write(response.read())
    print(f"[Real Model Test] Image saved locally to {save_path}")

def test_real_yolov8_inference():
    if YOLO is None:
        pytest.skip("ultralytics not installed")
    print("\n=======================================================")
    print("RUNNING REAL UN-MOCKED YOLOv8 MODEL INFERENCE")
    print("=======================================================")

    img_path = "sample_person_input.jpg"
    download_sample_real_image(img_path)

    # 1. Load real pre-trained YOLOv8 model (yolov8n.pt)
    print("[YOLOv8 Engine] Loading official 'yolov8n.pt' weights...")
    model = YOLO("yolov8n.pt")

    # 2. Run real model inference on the sample input image
    print(f"[YOLOv8 Engine] Executing model.predict() on '{img_path}'...")
    results = model.predict(source=img_path, conf=0.5)

    print("\n--- RAW UN-MOCKED YOLOv8 MODEL DETECTION OUTPUT ---")
    detections_found = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0].item())
            class_name = model.names[cls_id]
            confidence = float(box.conf[0].item())
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            x1, y1, x2, y2 = [round(val, 1) for val in xyxy]

            detection_info = {
                "class_label": class_name,
                "confidence_score": round(confidence, 4),
                "bounding_box": (x1, y1, x2, y2)
            }
            detections_found.append(detection_info)

            print(f"Detected Class: {class_name:<10} | Confidence: {confidence:.4f} | Bounding Box [x1, y1, x2, y2]: ({x1}, {y1}, {x2}, {y2})")

    print(f"\n[Summary] Total Un-Mocked Detections Extracted: {len(detections_found)}")
    assert len(detections_found) > 0
    print("=======================================================")

    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    run_real_yolov8_inference()
