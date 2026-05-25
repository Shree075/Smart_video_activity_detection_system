
from ultralytics import YOLO
import numpy as np

def main():
    # ===== YOUR NEW MODEL =====
    NEW_MODEL_PATH = r"E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect_v5\classes_smoking_violence\weights\best.pt"
    print(f"Loading model: {NEW_MODEL_PATH}")
    model = YOLO(NEW_MODEL_PATH)
    
    # ===== TEST SET EVALUATION =====
    metrics = model.val(
        data=r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\data.yaml",
        split="test",
        imgsz=640,
        batch=4,
        workers=0,
        plots=True
    )
    
    # ===== ALL METRICS =====
    print("\n" + "="*60)
    print("📊 6-CLASS MODEL - TEST SET RESULTS")
    print("="*60)
    print(f"mAP@0.5:        {metrics.box.map50:.3f}")
    print(f"mAP@0.5:0.95:   {metrics.box.map:.3f}")
    print(f"Precision:      {metrics.box.mp:.3f}")
    print(f"Recall:         {metrics.box.mr:.3f}")
    print(f"F1 Score:       {np.mean(metrics.box.f1):.3f}")  # FIXED!
    
    # ===== CLASS-WISE mAP =====
    print("\n📈 CLASS-WISE mAP50:")
    class_names = model.names
    for i, mAP in enumerate(metrics.box.maps):
        print(f"  {class_names[i]:10s}: {mAP:.3f}")
    
    print(f"\n✅ Plots saved: runs/detect/val/confusion_matrix.png")
    print("🎯 New model ready: " + NEW_MODEL_PATH)

if __name__ == "__main__":
    main()