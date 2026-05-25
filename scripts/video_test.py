from ultralytics import YOLO
import cv2

# 1. Load your model
model = YOLO(r"E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect_v5\classes_smoking_violence\weights\best.pt")

# 2. Run prediction using a generator to control the window
results = model.predict(
    source=r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\fighting.mp4",
    stream=True,  # Use stream=True for better memory management with CV2
    conf=0.4,
    save=True
)

for r in results:
    img = r.plot()  # This gets the frame with boxes drawn on it
    
    # RESIZE THE DISPLAY: Adjust (1280, 720) to fit your screen
    # This prevents the "zoomed in" effect by scaling the window down
    preview_img = cv2.resize(img, (1280, 720)) 
    
    cv2.imshow("Smart Detection System - Scaled Preview", preview_img)

    # Press 'q' to quit the video early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()