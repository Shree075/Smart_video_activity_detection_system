import os
import subprocess
import tkinter.messagebox as messagebox
from logger import SNAPSHOT_DIR, get_report_path


class ReportManager:
    def __init__(self, session_counts, log_callback=None):
        self.session_counts = session_counts
        self.log_callback = log_callback

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def open_snapshots(self):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        subprocess.Popen(f'explorer "{SNAPSHOT_DIR}"')
        self.log("📂 Snapshots folder opened.")

    def open_report(self):
        path = get_report_path()
        if os.path.exists(path):
            os.startfile(path)
            self.log("📋 CSV report opened.")
        else:
            self.log("⚠️ No report yet for today.")

    def show_summary(self):
        if not self.session_counts:
            messagebox.showinfo(
                "Session Summary",
                "No detections recorded in this session yet."
            )
            return

        total = sum(self.session_counts.values())
        lines = [f"{'─'*30}", "  SESSION SUMMARY", f"{'─'*30}"]

        for label, count in sorted(self.session_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {label.upper():<15} : {count} detections")

        lines.append(f"{'─'*30}")
        lines.append(f"  TOTAL : {total} detections")
        lines.append(f"{'─'*30}")

        messagebox.showinfo("Session Summary", "\n".join(lines))