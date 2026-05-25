from ultralytics import YOLO

def main():
    model = YOLO(r"E:\Final_Year_Project\Smart_video_activity_detection_system\runs\detect\train\weights\best.pt")

    metrics = model.val(
        data=r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\data.yaml",
        imgsz=640,
        batch=4,
        workers=0   # IMPORTANT for Windows
    )

    print("mAP@0.5:", metrics.box.map50)
    print("mAP@0.5:0.95:", metrics.box.map)
    print("Precision:", metrics.box.mp)
    print("Recall:", metrics.box.mr)

if __name__ == "__main__":
    main()



