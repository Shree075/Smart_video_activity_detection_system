import cv2
import math
from ultralytics import YOLO

class ActivityDetector:
    def __init__(self):
        self.item_model = YOLO(r'E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect_v5\classes_smoking_violence\weights\best.pt')
        self.pose_model = YOLO('yolov8n-pose.pt')

    def get_dist(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def process_frame(self, frame):
        """
        Takes a raw frame.
        Returns annotated frame + list of danger detections.
        Each detection = (label, confidence)
        """
        item_results = self.item_model(frame, conf=0.3, verbose=False)
        pose_results = self.pose_model(frame, verbose=False)

        # ── Get keypoints ────────────────────────────────────────────────────
        keypoints = None
        for pr in pose_results:
            if pr.keypoints is not None and len(pr.keypoints.xy) > 0:
                keypoints = pr.keypoints.xy.cpu().numpy()[0]

        danger_detections = []   # list of (label, conf) that are dangerous

        # ── Process each detected object ─────────────────────────────────────
        for ir in item_results:
            for box in ir.boxes:
                b      = box.xyxy[0].cpu().numpy().astype(int)
                label  = self.item_model.names[int(box.cls[0])].lower()
                conf   = float(box.conf[0])
                center = ((b[0]+b[2])/2, (b[1]+b[3])/2)

                is_danger = False

                if keypoints is not None and len(keypoints) > 10:
                    dist_h = min(
                        self.get_dist(keypoints[9],  center),
                        self.get_dist(keypoints[10], center)
                    )
                    dist_f = self.get_dist(keypoints[0], center)

                    if label in ['gun', 'knife', 'violence','grenade'] and dist_h < 110:
                        is_danger = True
                    if label in ['cigarette', 'alcohol', 'smoking'] and dist_f < 80:
                        is_danger = True

                else:
                    # Fallback — no pose detected, trigger on object alone
                    if label in ['gun', 'knife', 'violence','grenade',
                                 'cigarette', 'alcohol', 'smoking']:
                        is_danger = True

                # ── Draw bounding box ─────────────────────────────────────
                color = (0, 0, 255) if is_danger else (0, 255, 0)
                cv2.rectangle(frame, (b[0], b[1]), (b[2], b[3]), color, 3)
                cv2.putText(
                    frame,
                    f"{label} {conf:.2f}",
                    (b[0], b[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                )

                # ── Collect danger detections ─────────────────────────────
                if is_danger:
                    danger_detections.append((label, conf))

        return frame, danger_detections