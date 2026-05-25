import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

# Import your new modules
from alarm_manager import AlarmManager
from report_manager import ReportManager
from source_manager import SourceManager
from detector import ActivityDetector
from alert import trigger_alert
from logger import record_detection

class SurveillanceApp:
    def __init__(self, window):
        self.window = window
        self.window.title("FYP Smart Surveillance")
        self.window.geometry("1200x950")
        self.window.configure(bg="#2c3e50")

        # Initialize Components
        self.alarm = AlarmManager()
        self.reports = ReportManager()
        self.sources = SourceManager()
        self.detector = ActivityDetector()

        self.running = False
        self.setup_ui()

    def setup_ui(self):
        # Header & Stats Labels (Simplified for brevity)
        tk.Label(self.window, text="SMART DETECTION SYSTEM", font=("Helvetica", 20), bg="#2c3e50", fg="white").pack()
        
        self.stats_label = tk.Label(self.window, text="📊 Session: 0 detections", bg="#1a252f", fg="white")
        self.stats_label.pack(fill=tk.X)

        # Video Frame
        self.video_label = tk.Label(self.window, bg="black")
        self.video_label.pack(pady=10)

        # Buttons - Example Mapping
        btn_frame = tk.Frame(self.window, bg="#2c3e50")
        btn_frame.pack()

        tk.Button(btn_frame, text="📁 Browse", command=self.handle_browse).grid(row=0, column=0)
        tk.Button(btn_frame, text="▶ Start", command=self.start_monitoring).grid(row=0, column=1)
        tk.Button(btn_frame, text="⏹ Stop", command=self.stop_monitoring).grid(row=0, column=2)
        tk.Button(btn_frame, text="📋 Report", command=self.reports.open_csv).grid(row=0, column=3)

    def handle_browse(self):
        path = self.sources.select_file()
        if path: messagebox.showinfo("Source", f"Selected: {path}")

    def start_monitoring(self):
        if not self.running:
            self.cap = cv2.VideoCapture(self.sources.source)
            self.running = True
            threading.Thread(target=self.video_loop, daemon=True).start()

    def stop_monitoring(self):
        self.running = False

    def video_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret: break

            annotated_frame, detections = self.detector.process_frame(frame)

            for label, conf in detections:
                # Update stats via module
                total, summary = self.reports.update_stats(label)
                self.window.after(0, lambda: self.stats_label.config(text=f"📊 Session: {total} | {summary}"))
                
                # Trigger alarm via module
                self.alarm.trigger()
                
                # Run background alerts
                threading.Thread(target=record_detection, args=(frame.copy(), label, conf, self.sources.source_type), daemon=True).start()
                threading.Thread(target=trigger_alert, args=(label, conf, annotated_frame.copy()), daemon=True).start()

            # Display logic
            img = Image.fromarray(cv2.cvtColor(cv2.resize(annotated_frame, (800, 450)), cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

        self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SurveillanceApp(root)
    root.mainloop()