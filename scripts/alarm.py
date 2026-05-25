# run_once_generate_beep.py
import wave, struct, math

def generate_beep(filename="alarm.wav", frequency=1000, duration=1.0, volume=0.5, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(num_samples):
            # Create beeping pattern — on for 0.1s off for 0.1s
            cycle = i % (sample_rate // 5)
            if cycle < sample_rate // 10:
                value = int(volume * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            else:
                value = 0
            f.writeframes(struct.pack('<h', value))
    print(f"✅ alarm.wav generated!")

generate_beep("alarm.wav")