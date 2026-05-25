import cv2
import numpy as np
from ultralytics import YOLO
import math

def get_distance(p1, p2):
    """Calculates Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def main():
    # 1. LOAD MODELS
    item_model = YOLO(r'E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect\train\weights\best.pt')
    pose_model = YOLO('yolov8n-pose.pt')

    # 2. VIDEO SOURCE & WINDOW SETUP
    video_path = r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\knife2.mp4"
    cap = cv2.VideoCapture(video_path)

    # Persistence buffers to stop flickering
    smoke_timer = 0
    drink_timer = 0
    
    # FIX: Resizable window to prevent "Zoom" issues
    cv2.namedWindow("Smart Activity Monitor", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Smart Activity Monitor", 1280, 720)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # 3. RUN INFERENCE
        # Lower conf (0.2) helps catch the Knife and Cigarette more consistently
        item_results = item_model(frame, conf=0.2, verbose=False)
        pose_results = pose_model(frame, verbose=False)
        
        annotated_frame = frame.copy()
        current_alerts = []

        # 4. EXTRACT POSE DATA (Nose and Wrists)
        keypoints = None
        for pr in pose_results:
            if pr.keypoints is not None:
                kp = pr.keypoints.xy.cpu().numpy()
                if len(kp) > 0:
                    keypoints = kp[0] # Focus on the primary person

        # 5. DRAW ALL BOXES & RUN INTERACTION LOGIC
        for ir in item_results:
            for box in ir.boxes:
                # Basic info for every detected object
                b = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = item_model.names[cls_id].lower()
                center_obj = ((b[0]+b[2])/2, (b[1]+b[3])/2)

                # --- STEP A: DRAW BOX FOR EVERYTHING ---
                # Default color is Green (Safe/Detected)
                box_color = (0, 255, 0) 
                
                # --- STEP B: CHECK POSE INTERACTION ---
                if keypoints is not None and len(keypoints) > 10:
                    nose = keypoints[0]
                    l_wrist = keypoints[9]
                    r_wrist = keypoints[10]

                    # WEAPONS (Gun/Knife) - Hand proximity
                    if label in ['gun', 'knife']:
                        dist_hand = min(get_distance(l_wrist, center_obj), get_distance(r_wrist, center_obj))
                        if dist_hand < 120: # If hand is near the weapon
                            current_alerts.append(f"DANGER: {label.upper()} ARMED")
                            box_color = (0, 0, 255) # Turn box Red

                    # CIGARETTE - Mouth/Nose proximity
                    elif label == 'cigarette':
                        dist_nose = get_distance(nose, center_obj)
                        if dist_nose < 70: 
                            smoke_timer = 30 # Persistent alert for 30 frames
                            box_color = (0, 165, 255) # Orange

                    # ALCOHOL - Mouth or Hand proximity
                    elif label == 'alcohol':
                        dist_nose = get_distance(nose, center_obj)
                        dist_hand = min(get_distance(l_wrist, center_obj), get_distance(r_wrist, center_obj))
                        if dist_nose < 100 or dist_hand < 80:
                            drink_timer = 30
                            box_color = (255, 0, 0) # Blue

                # Draw the actual box and label on the frame for EVERY class
                cv2.rectangle(annotated_frame, (b[0], b[1]), (b[2], b[3]), box_color, 2)
                cv2.putText(annotated_frame, f"{label} {conf:.2f}", (b[0], b[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

        # 6. OVERLAY SMART ALERTS (Persistence Logic)
        if smoke_timer > 0:
            current_alerts.append("ACTIVITY: SMOKING")
            smoke_timer -= 1
        if drink_timer > 0:
            current_alerts.append("ACTIVITY: DRINKING")
            drink_timer -= 1

        # Display alerts in the top corner
        for i, text in enumerate(set(current_alerts)):
            cv2.putText(annotated_frame, text, (30, 50 + (i * 40)), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 3)

        # 7. SHOW FINAL OUTPUT
        cv2.imshow("Smart Activity Monitor", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()