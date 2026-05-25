from ultralytics import YOLO
import os

if __name__ == "__main__":
    # Load your PREVIOUS best model (faster convergence)
    model = YOLO(r"E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect\train\weights\best.pt")
  # CHANGE: Use your old weights!
    
    # Train the model
    model.train(
        task="detect",
        data=r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\data.yaml",  # Raw string for Windows paths
        epochs=60,  # CHANGE: 60 instead of 100 (with patience it will stop early)
        imgsz=640,
        batch=4,
        workers=0,
        patience=12,  # NEW: Auto-stop if no improvement
        device=0,     # NEW: Explicit GPU
        project="runs/detect_v5",  # NEW: Separate folder for new training
        name="6_classes_smoking_violence"  # NEW: Clear name
    )
