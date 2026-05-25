from flask import Flask, render_template, jsonify, send_from_directory, request
import os
import csv
import time

app = Flask(__name__)

# ─── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR     = r"E:\Final_Year_Project\Smart_video_activity_detection_system"
SNAPSHOT_DIR = os.path.join(BASE_DIR, "snapshots")
REPORT_DIR   = os.path.join(BASE_DIR, "reports")

def get_report_path(date_str):
    return os.path.join(REPORT_DIR, f"detection_report_{date_str}.csv")

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/dates")
def get_available_dates():
    """
    Returns list of all dates that have a report CSV.
    Used to populate the date picker dropdown.
    """
    if not os.path.exists(REPORT_DIR):
        return jsonify({"dates": []})

    dates = []
    for f in sorted(os.listdir(REPORT_DIR), reverse=True):
        if f.startswith("detection_report_") and f.endswith(".csv"):
            date_str = f.replace("detection_report_", "").replace(".csv", "")
            dates.append(date_str)

    return jsonify({"dates": dates})

@app.route("/api/alerts")
def get_alerts():
    """
    Returns detections for a specific date.
    Date passed as query param: /api/alerts?date=2025-04-03
    Defaults to today if no date given.
    """
    date_str = request.args.get("date", time.strftime("%Y-%m-%d"))
    path     = get_report_path(date_str)
    alerts   = []

    if not os.path.exists(path):
        return jsonify({"alerts": [], "stats": {}, "date": date_str})

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alerts.append(row)

    alerts.reverse()

    stats = {}
    for alert in alerts:
        cls        = alert.get("Threat Class", "Unknown")
        stats[cls] = stats.get(cls, 0) + 1

    return jsonify({"alerts": alerts, "stats": stats, "date": date_str})

@app.route("/api/snapshots")
def get_snapshots():
    """
    Returns snapshots for a specific date.
    Date passed as query param: /api/snapshots?date=2025-04-03
    """
    date_str = request.args.get("date", time.strftime("%Y-%m-%d"))

    if not os.path.exists(SNAPSHOT_DIR):
        return jsonify({"snapshots": []})

    # Filter snapshots by date in filename
    files = sorted(
        [f for f in os.listdir(SNAPSHOT_DIR)
         if f.endswith(".jpg") and date_str in f],
        reverse=True
    )[:12]

    return jsonify({"snapshots": files, "date": date_str})

@app.route("/snapshots/<filename>")
def serve_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename)

if __name__ == "__main__":
    print("✅ Dashboard running at: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)