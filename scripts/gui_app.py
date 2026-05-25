import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time

from detector import ActivityDetector
from alert import trigger_alert
from logger import record_detection
from alarm_manager import AlarmManager
from source_manager import SourceManager
from report_manager import ReportManager


class SurveillanceApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1200x950")
        self.window.configure(bg="#2c3e50")

        self.detector = ActivityDetector()

        self.running = False
        self.cap = None
        self.thread = None
        self.session_counts = {}

        self.source_manager = SourceManager(
            log_callback=self.add_log,
            source_label_callback=self.update_source_label
        )

        self.alarm_manager = AlarmManager(
            log_callback=self.add_log
        )

        self.report_manager = ReportManager(
            self.session_counts,
            log_callback=self.add_log
        )

        self.video_source = self.source_manager.video_source
        self.source_type = self.source_manager.source_type

        self.setup_ui()

    def setup_ui(self):
        tk.Label(
            self.window,
            text="SMART VIDEO ACTIVITY DETECTION SYSTEM",
            font=("Helvetica", 24, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=20
        ).pack(fill=tk.X)

        self.source_label = tk.Label(
            self.window,
            text="📁 Source: Video File",
            font=("Helvetica", 11),
            bg="#1a252f",
            fg="#1abc9c",
            pady=5
        )
        self.source_label.pack(fill=tk.X)

        self.alarm_status_label = tk.Label(
            self.window,
            text="🔔 Sound Alarm: ON",
            font=("Helvetica", 11),
            bg="#1a252f",
            fg="#f39c12",
            pady=4
        )
        self.alarm_status_label.pack(fill=tk.X)

        self.stats_label = tk.Label(
            self.window,
            text="📊 Session: 0 detections",
            font=("Helvetica", 11),
            bg="#1a252f",
            fg="#3498db",
            pady=4
        )
        self.stats_label.pack(fill=tk.X)

        self.main_frame = tk.Frame(self.window, bg="#2c3e50")
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        self.video_label = tk.Label(
            self.main_frame,
            bg="black",
            width=850,
            height=500
        )
        self.video_label.grid(row=0, column=0, padx=10)

        self.alert_frame = tk.LabelFrame(
            self.main_frame,
            text="Real-time Alerts",
            font=("Helvetica", 14, "bold"),
            bg="#34495e",
            fg="white",
            padx=10,
            pady=10
        )
        self.alert_frame.grid(row=0, column=1, sticky="nsew")

        self.alert_list = tk.Listbox(
            self.alert_frame,
            width=35,
            height=16,
            bg="#ecf0f1",
            font=("Courier", 10)
        )
        self.alert_list.pack()

        source_frame = tk.Frame(self.window, bg="#2c3e50", pady=5)
        source_frame.pack()

        tk.Button(
            source_frame,
            text="📁 Browse Video File",
            command=self.handle_browse_video,
            bg="#2980b9",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=20
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            source_frame,
            text="📷 Use Webcam",
            command=self.handle_use_webcam,
            bg="#8e44ad",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=20
        ).grid(row=0, column=1, padx=8)

        control_frame = tk.Frame(self.window, bg="#2c3e50", pady=5)
        control_frame.pack()

        tk.Button(
            control_frame,
            text="▶ START MONITORING",
            command=self.start,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=18
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            control_frame,
            text="⏹ STOP",
            command=self.stop,
            bg="#c0392b",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=18
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            control_frame,
            text="🗑 Clear Logs",
            command=self.clear_logs,
            bg="#7f8c8d",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=18
        ).grid(row=0, column=2, padx=6)

        alarm_frame = tk.Frame(self.window, bg="#2c3e50", pady=5)
        alarm_frame.pack()

        tk.Button(
            alarm_frame,
            text="🔔 Toggle Alarm ON/OFF",
            command=self.handle_toggle_alarm,
            bg="#d35400",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=22
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            alarm_frame,
            text="🔊 Test Alarm",
            command=self.alarm_manager.test_alarm,
            bg="#16a085",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=16
        ).grid(row=0, column=1, padx=6)

        report_frame = tk.Frame(self.window, bg="#2c3e50", pady=5)
        report_frame.pack()

        tk.Button(
            report_frame,
            text="📂 Open Snapshots Folder",
            command=self.report_manager.open_snapshots,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=22
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            report_frame,
            text="📋 Open CSV Report",
            command=self.report_manager.open_report,
            bg="#2980b9",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=22
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            report_frame,
            text="📊 Session Summary",
            command=self.report_manager.show_summary,
            bg="#8e44ad",
            fg="white",
            font=("Helvetica", 11, "bold"),
            width=22
        ).grid(row=0, column=2, padx=6)

    def update_source_label(self, text, color):
        self.source_label.configure(text=text, fg=color)

    def handle_browse_video(self):
        source, source_type = self.source_manager.browse_video(self.running)
        if source is not None:
            self.video_source = source
            self.source_type = source_type

    def handle_use_webcam(self):
        source, source_type = self.source_manager.use_webcam(self.running)
        if source is not None:
            self.video_source = source
            self.source_type = source_type

    def handle_toggle_alarm(self):
        status = self.alarm_manager.toggle_alarm()
        if status:
            self.alarm_status_label.configure(
                text="🔔 Sound Alarm: ON",
                fg="#f39c12"
            )
        else:
            self.alarm_status_label.configure(
                text="🔕 Sound Alarm: OFF",
                fg="#7f8c8d"
            )

    def update_stats(self, label):
        self.session_counts[label] = self.session_counts.get(label, 0) + 1
        total = sum(self.session_counts.values())
        summary = "  |  ".join(
            [f"{k.upper()}: {v}" for k, v in self.session_counts.items()]
        )
        self.stats_label.configure(
            text=f"📊 Session: {total} detections  —  {summary}"
        )

    def start(self):
        if not self.running:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                self.add_log("❌ Error: Cannot open video source!")
                messagebox.showerror("Source Error", "Cannot open selected video source.")
                return

            self.running = True
            self.thread = threading.Thread(target=self.video_loop, daemon=True)
            self.thread.start()

            if self.source_type == "webcam":
                self.add_log("✅ Webcam monitoring started...")
            else:
                self.add_log("✅ Video monitoring started...")

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.add_log("🔴 Monitoring stopped.")

    def clear_logs(self):
        self.alert_list.delete(0, tk.END)

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.alert_list.insert(0, f"[{timestamp}] {message}")

    def video_loop(self):
        while self.running:
            if self.cap is None:
                break

            ret, frame = self.cap.read()

            if not ret:
                if self.source_type == "webcam":
                    continue
                else:
                    self.window.after(0, self.add_log, "✅ Video ended.")
                    self.running = False
                    break

            annotated_frame, danger_detections = self.detector.process_frame(frame)

            for label, conf in danger_detections:
                threading.Thread(
                    target=record_detection,
                    args=(frame.copy(), label, conf, self.source_type),
                    daemon=True
                ).start()

                self.window.after(0, self.update_stats, label)

                self.window.after(
                    0,
                    self.add_log,
                    f"🚨 {label.upper()} ({conf:.2f}) — snapshot saved"
                )

                self.alarm_manager.trigger_alarm_sound()

                threading.Thread(
                    target=trigger_alert,
                    args=(label, conf, annotated_frame.copy()),
                    daemon=True
                ).start()

            source_text = "LIVE WEBCAM" if self.source_type == "webcam" else "VIDEO FILE"
            color_text = (0, 0, 255) if self.source_type == "webcam" else (0, 255, 0)

            cv2.putText(
                annotated_frame,
                f"● {source_text}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color_text,
                2
            )

            cv2.putText(
                annotated_frame,
                time.strftime("%Y-%m-%d %H:%M:%S"),
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )

            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (850, 500))
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        if self.cap:
            self.cap.release()
            self.cap = None


if __name__ == "__main__":
    root = tk.Tk()
    app = SurveillanceApp(root, "FYP Activity Detector")
    app.start()
    root.mainloop()
