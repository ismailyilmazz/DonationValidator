import time
import subprocess
import os
import signal
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class RestartHandler(PatternMatchingEventHandler):
    def __init__(self, command, debounce_delay=1.0):
        super().__init__(
            patterns=["*.py"],
            ignore_directories=True,
            ignore_patterns=["*/__pycache__/*", "*.pyc", "*.pyo"]
        )
        self.command = command
        self.process = None
        self.debounce_delay = debounce_delay
        self.last_event_time = 0
        self.restart_server()

    def restart_server(self):
        if self.process:
            print("🛑 Sunucu durduruluyor...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                print("⚠️ Zorla öldürülüyor...")
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()

        time.sleep(1)  # Portun tam kapanmasını bekle
        print("🚀 Sunucu başlatılıyor...")
        self.process = subprocess.Popen(
            self.command,
            shell=True,
            preexec_fn=os.setsid
        )
        self.last_event_time = time.time()

    def on_modified(self, event):
        now = time.time()
        if now - self.last_event_time > self.debounce_delay:
            print(f"🔄 Değişiklik algılandı: {event.src_path}")
            self.restart_server()

if __name__ == "__main__":
    path = "."  # proje kökü
    command = "/home/abdullah/okul/venv/bin/daphne odev.asgi:application"
    event_handler = RestartHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print("👁‍🗨 Watchdog izliyor...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🧹 Watchdog durduruluyor...")
        observer.stop()
        if event_handler.process:
            try:
                os.killpg(os.getpgid(event_handler.process.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
    observer.join()
