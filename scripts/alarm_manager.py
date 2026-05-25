import os
import time
import threading

try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


ALARM_SOUND_PATH = os.path.join(os.path.dirname(__file__), "alarm.wav")


class AlarmManager:
    def __init__(self, log_callback=None):
        self.alarm_enabled = True
        self.alarm_playing = False
        self.alarm_cooldown = 10
        self.last_alarm_time = 0
        self.log_callback = log_callback

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def toggle_alarm(self):
        self.alarm_enabled = not self.alarm_enabled
        if self.alarm_enabled:
            self.log("🔔 Sound alarm ON")
            return True
        else:
            self.log("🔕 Sound alarm OFF")
            return False

    def test_alarm(self):
        self.log("🔊 Testing alarm...")
        threading.Thread(target=self._play_sound, daemon=True).start()

    def _play_sound(self):
        if not SOUND_AVAILABLE:
            self.log("❌ playsound not installed.")
            return
        if not os.path.exists(ALARM_SOUND_PATH):
            self.log("❌ alarm.wav not found!")
            return
        try:
            playsound(ALARM_SOUND_PATH)
        except Exception as e:
            self.log(f"❌ Sound Error: {e}")

    def trigger_alarm_sound(self):
        if not self.alarm_enabled or self.alarm_playing:
            return
        now = time.time()
        if now - self.last_alarm_time < self.alarm_cooldown:
            return

        self.last_alarm_time = now
        self.alarm_playing = True

        def play_and_reset():
            self._play_sound()
            self.alarm_playing = False

        threading.Thread(target=play_and_reset, daemon=True).start()