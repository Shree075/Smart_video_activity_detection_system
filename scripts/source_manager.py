from tkinter import filedialog


class SourceManager:
    def __init__(self, log_callback=None, source_label_callback=None):
        self.video_source = r"E:\Final_Year_Project\Smart_video_activity_detection_system\dataset\knife2.mp4"
        self.source_type = "video"
        self.log_callback = log_callback
        self.source_label_callback = source_label_callback

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def update_source_label(self, text, color):
        if self.source_label_callback:
            self.source_label_callback(text, color)

    def browse_video(self, running=False):
        if running:
            self.log("⚠️ Stop monitoring before changing source.")
            return None, None

        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        )

        if path:
            self.video_source = path
            self.source_type = "video"
            filename = path.replace("\\", "/").split("/")[-1]
            self.update_source_label(f"📁 Source: {filename}", "#1abc9c")
            self.log(f"📁 Video: {filename}")

        return self.video_source, self.source_type

    def use_webcam(self, running=False):
        if running:
            self.log("⚠️ Stop monitoring before changing source.")
            return None, None

        self.video_source = 0
        self.source_type = "webcam"
        self.update_source_label("📷 Source: Live Webcam", "#e74c3c")
        self.log("📷 Webcam selected.")
        return self.video_source, self.source_type