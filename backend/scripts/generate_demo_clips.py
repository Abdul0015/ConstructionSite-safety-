import os
import cv2
import numpy as np

DEMO_CLIPS_DIR = "storage/demo_clips"

def generate_clip(filename: str, num_frames: int = 30, text_overlay: str = "Demo Clip", dark_mode: bool = False):
    os.makedirs(DEMO_CLIPS_DIR, exist_ok=True)
    filepath = os.path.join(DEMO_CLIPS_DIR, filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, 10.0, (640, 480))

    for i in range(num_frames):
        if dark_mode:
            # Low light/dark scene frame
            frame = np.full((480, 640, 3), 15, dtype=np.uint8)
        else:
            # Daytime site frame
            frame = np.full((480, 640, 3), 200, dtype=np.uint8)
            # Draw ground grid line
            cv2.line(frame, (0, 300), (640, 300), (0, 0, 255), 2)

        # Annotate clip description
        cv2.putText(frame, f"{text_overlay} - Frame {i+1}/{num_frames}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255) if dark_mode else (0, 0, 0), 2)

        out.write(frame)

    out.release()
    print(f"[Demo Clip Generator] Generated real MP4 video file: {filepath} ({num_frames} frames)")

if __name__ == "__main__":
    generate_clip("demo_no_helmet.mp4", text_overlay="Clip 1: No Helmet Violation")
    generate_clip("demo_compliant.mp4", text_overlay="Clip 2: Compliant PPE Worker")
    generate_clip("demo_vehicle_entry.mp4", text_overlay="Clip 3: Vehicle Gate Crossing y=300")
    generate_clip("demo_restricted_zone.mp4", text_overlay="Clip 4: Restricted Zone Polygon Entry")
    generate_clip("demo_low_light_limitation.mp4", text_overlay="Clip 5: Low Light Occlusion Limitation", dark_mode=True)
