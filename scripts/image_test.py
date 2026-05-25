from ultralytics import YOLO

# Load trained model
model = YOLO(r"E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect\train\weights\best.pt")

# Perform inference on test images
results = model.predict(
    source=r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\test\images",
    show=True,
    save=True,
    conf=0.5
)
