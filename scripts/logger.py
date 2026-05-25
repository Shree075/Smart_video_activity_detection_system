import csv
import os
import time
import cv2

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
BASE_DIR      = r"E:\Final_Year_Project\Smart_video_activity_detection_system"
SNAPSHOT_DIR  = os.path.join(BASE_DIR, "snapshots")
REPORT_DIR    = os.path.join(BASE_DIR, "reports")

# Create folders if they don't exist
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR,   exist_ok=True)

# CSV report file — one per day
def get_report_path():
    date_str = time.strftime("%Y-%m-%d")
    return os.path.join(REPORT_DIR, f"detection_report_{date_str}.csv")

# ─── INITIALIZE CSV ───────────────────────────────────────────────────────────
def init_csv():
    """Create CSV file with headers if it doesn't exist yet."""
    path = get_report_path()
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Date",
                "Time",
                "Threat Class",
                "Confidence",
                "Snapshot File",
                "Source"
            ])
        print(f"✅ CSV report created: {path}")
    return path

# ─── SAVE SNAPSHOT ────────────────────────────────────────────────────────────
def save_snapshot(frame, label):
    """
    Saves a JPEG snapshot of the detection.
    Returns the filename.
    """
    timestamp    = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename     = f"{label}_{timestamp}.jpg"
    filepath     = os.path.join(SNAPSHOT_DIR, filename)
    cv2.imwrite(filepath, frame)
    print(f"📸 Snapshot saved: {filename}")
    return filename

# ─── LOG TO CSV ───────────────────────────────────────────────────────────────
def log_detection(label, confidence, snapshot_filename, source_type):
    """
    Appends one detection row to today's CSV report.
    """
    path = get_report_path()
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d"),
            time.strftime("%H:%M:%S"),
            label.upper(),
            f"{confidence:.2f}",
            snapshot_filename,
            source_type.upper()
        ])
    print(f"📋 Detection logged to CSV: {label.upper()}")

# ─── COMBINED FUNCTION ────────────────────────────────────────────────────────
def record_detection(frame, label, confidence, source_type):
    """
    Master function — call this on every danger detection.
    Saves snapshot + logs to CSV in one call.
    """
    snapshot_filename = save_snapshot(frame, label)
    init_csv()
    log_detection(label, confidence, snapshot_filename, source_type)
    return snapshot_filename