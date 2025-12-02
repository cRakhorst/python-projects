import pyaudio
import numpy as np
import psutil
import time
import pygetwindow as gw
import win32gui
import win32process

def close_focused_app():
    try:
        hwnd = win32gui.GetForegroundWindow()  # handle van de actieve window
        if hwnd == 0:
            print("No active window detected.")
            return

        # Haal PID van die window op
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        proc_name = proc.name().lower()

        # Haal titel van het venster (voor debug)
        title = win32gui.GetWindowText(hwnd)

        # Skip consoles en python-processen
        if any(skip in proc_name for skip in ["cmd.exe", "python.exe", "pythonw.exe", "powershell.exe"]):
            print(f"Skipping console or Python process: {proc.name()}")
            return

        print(f"Closing {proc.name()} (PID {pid}) - {title}")
        proc.terminate()

    except Exception as e:
        print(f"Error closing app: {e}")

def detect_sound(threshold=500, chunk=1024, rate=44100, loudsound=6000):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Listening for sound...")

    action_triggered = False

    try:
        while True:
            data = np.frombuffer(stream.read(chunk), dtype=np.int16)
            peak = np.abs(data).max()

            if peak > threshold:
                print(f"Sound detected with peak: {peak}")

            if peak > loudsound and not action_triggered:
                print(f"Loud sound detected with peak: {peak}")
                close_focused_app()
                action_triggered = True
            elif peak < loudsound and action_triggered:
                action_triggered = False

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping sound detection.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    detect_sound()
