import smtplib
import time
import requests
import cv2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage



# ─── CONFIGURATION ───────────────────────────────────────────────────────────
EMAIL_SENDER       = "videoactivitydetect@gmail.com"
EMAIL_PASSWORD     = "rsyn wbkc wwlo jsci"
EMAIL_RECEIVER     = "shreeyashpawar75@gmail.com"

ULTRAMSG_INSTANCE  = "instance176277"   # e.g. instance12345
ULTRAMSG_TOKEN     = "9afodhvbng2xnq4a"          # from UltraMsg dashboard
WHATSAPP_TO        = "919561696060"        # your number with country code, no +

COOLDOWN_SECONDS   = 30
last_alert_time    = {}

# ─── WHATSAPP ─────────────────────────────────────────────────────────────────
def send_whatsapp(label, confidence):
    try:
        url     = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
        payload = {
            "token" : ULTRAMSG_TOKEN,
            "to"    : WHATSAPP_TO,
            "body"  : (
                f"🚨 SECURITY ALERT\n"
                f"─────────────────\n"
                f"Threat    : {label.upper()}\n"
                f"Confidence: {confidence:.2f}\n"
                f"Time      : {time.ctime()}\n"
                f"─────────────────\n"
                f"Check camera immediately!"
            )
        }
        response = requests.post(url, data=payload, timeout=10)
        result   = response.json()
        if result.get("sent") == "true":
            print("✅ WhatsApp alert sent!")
        else:
            print(f"⚠️ WhatsApp response: {result}")
    except Exception as e:
        print(f"❌ WhatsApp Error: {e}")

# ─── EMAIL ────────────────────────────────────────────────────────────────────
def send_email(label, confidence, frame):
    try:
        msg            = MIMEMultipart()
        msg["Subject"] = f"🚨 SECURITY ALERT: {label.upper()} Detected"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        body = f"""
        <html><body>
        <h2 style="color:red;">⚠️ Anomalous Activity Detected</h2>
        <table border="1" cellpadding="8" cellspacing="0">
          <tr><td><b>Threat</b></td><td>{label.upper()}</td></tr>
          <tr><td><b>Confidence</b></td><td>{confidence:.2f}</td></tr>
          <tr><td><b>Time</b></td><td>{time.ctime()}</td></tr>
        </table>
        <br>
        <p>Snapshot of the detection is attached.</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html"))

        _, img_encoded = cv2.imencode(".jpg", frame)
        attachment     = MIMEImage(img_encoded.tobytes(), name="snapshot.jpg")
        msg.attach(attachment)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email alert sent!")

    except Exception as e:
        print(f"❌ Email Error: {e}")

# ─── MASTER TRIGGER ───────────────────────────────────────────────────────────
def trigger_alert(label, confidence, frame):
    """
    Call this function from anywhere.
    It checks cooldown then fires Email + WhatsApp.
    """
    now = time.time()
    if now - last_alert_time.get(label, 0) < COOLDOWN_SECONDS:
        return  # Still in cooldown

    last_alert_time[label] = now
    print(f"🚨 ALERT TRIGGERED: {label.upper()} ({confidence:.2f})")

    #add_web_alert(label, confidence, source="GUI Detection")
    send_email(label, confidence, frame)
    send_whatsapp(label, confidence)