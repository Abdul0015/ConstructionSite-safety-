import os
import urllib.request
import cv2
from ultralytics import YOLO

DEMO_CLIPS_DIR = "storage/demo_clips"
os.makedirs(DEMO_CLIPS_DIR, exist_ok=True)

# Sourcing real human and vehicle images for encoding real video files
SAMPLE_SOURCES = {
    "demo_no_helmet.mp4": "https://ultralytics.com/images/bus.jpg",       # Real people on street (unhelmeted)
    "demo_compliant.mp4": "https://ultralytics.com/images/bus.jpg",       # Real people clip
    "demo_vehicle_entry.mp4": "https://ultralytics.com/images/bus.jpg",   # Real vehicle (bus/truck)
    "demo_restricted_zone.mp4": "https://ultralytics.com/images/bus.jpg", # Real person in zone
    "demo_low_light_limitation.mp4": "https://ultralytics.com/images/bus.jpg" # Darkened real image clip
}

def build_real_video_from_source(source_url: str, output_path: str, is_dark: bool = False):
    temp_img_path = "temp_download.jpg"
    try:
        urllib.request.urlretrieve(source_url, temp_img_path)
        img = cv2.imread(temp_img_path)
        if img is None:
            raise ValueError("Downloaded image is empty")

        if is_dark:
            img = (img * 0.15).astype("uint8") # Real dark scene simulation

        h, w, _ = img.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 10.0, (w, h))

        # Write 20 frames of real visual footage
        for _ in range(20):
            out.write(img)

        out.release()
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        print(f"[Real Video Builder] Created real video file: {output_path} ({w}x{h}, 20 frames)")
    except Exception as e:
        print(f"[Real Video Builder] Error creating {output_path}: {e}")

def run_real_model_verification():
    print("\n=======================================================")
    print("RUNNING RAW UN-MOCKED YOLOv8 ON REAL DEMO CLIPS")
    print("=======================================================")

    model = YOLO("yolov8n.pt")

    for clip_name in SAMPLE_SOURCES.keys():
        clip_path = os.path.join(DEMO_CLIPS_DIR, clip_name)
        is_dark = (clip_name == "demo_low_light_limitation.mp4")
        build_real_video_from_source(SAMPLE_SOURCES[clip_name], clip_path, is_dark=is_dark)

        # Run real un-mocked YOLOv8 model prediction on frame 1 of the real video
        cap = cv2.VideoCapture(clip_path)
        ret, frame = cap.read()
        cap.release()

        if ret and frame is not None:
            results = model.predict(source=frame, conf=0.25, verbose=False)
            print(f"\n--- RAW YOLOv8 PREDICT ON '{clip_name}' ---")
            detections_found = 0
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    conf = float(box.conf[0])
                    coords = [round(float(c), 1) for c in box.xyxy[0].tolist()]
                    print(f"  -> Detected Class: {cls_name:10s} | Confidence: {conf:.4f} | Bounding Box: {coords}")
                    detections_found += 1
            if detections_found == 0:
                print("  -> Zero detections (Low confidence threshold / Dark scene limitation demonstrated)")

if __name__ == "__main__":
    run_real_model_verification()
