from ultralytics import YOLO

if __name__ == "__main__":
    # Load YOLOv8 model
    model = YOLO("yolov8n.pt")

    # Train the model
    model.train(
        task="detect",
        data="E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\data.yaml",     # path to your data.yaml
        epochs=100,
        imgsz=640,
        batch=4,
        workers=0
    )