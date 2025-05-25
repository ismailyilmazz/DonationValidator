import time
import subprocess
import os
import signal
import platform
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys

class RestartHandler(PatternMatchingEventHandler):
    def __init__(self, command, debounce_delay=1.0):
        super().__init__(
            patterns=["*.py", "*.html", "*.css", "*.js"],  # hangi dosyaları izleyeceğiz
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
                if platform.system() == "Windows":
                    self.process.terminate()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                print("⚠️ Zorla öldürülüyor...")
                if platform.system() == "Windows":
                    self.process.kill()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()
            except Exception as e:
                print(f"❌ Durdurma hatası: {e}")

        time.sleep(1)  # Portun kapanmasını bekle
        print("🚀 Sunucu başlatılıyor...")

        try:
            if platform.system() == "Windows":
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    preexec_fn=os.setsid
                )
            self.last_event_time = time.time()
        except Exception as e:
            print(f"❌ Başlatma hatası: {e}")

    def on_modified(self, event):
        now = time.time()
        if now - self.last_event_time > self.debounce_delay:
            print(f"🔄 Değişiklik algılandı: {event.src_path}")
            self.restart_server()

if __name__ == "__main__":
    path = "."
    
    python_executable = sys.executable
    command = f'"{python_executable}" -m daphne odev.asgi:application'

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
                if platform.system() == "Windows":
                    event_handler.process.terminate()
                else:
                    os.killpg(os.getpgid(event_handler.process.pid), signal.SIGTERM)
            except Exception as e:
                print(f"❌ Temizleme hatası: {e}")
    observer.join()
