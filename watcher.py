import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart_server()

    def restart_server(self):
        if self.process:
            print("🛑 Sunucu durduruluyor...")
            self.process.terminate()
            self.process.wait()
        print("🚀 Sunucu başlatılıyor...")
        self.process = subprocess.Popen(self.command, shell=True)

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 Değişiklik algılandı: {event.src_path}")
            self.restart_server()

if __name__ == "__main__":
    path = "."  # Proje kökü
    command = "daphne odev.asgi:application"  # Başlatılacak komut
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
            event_handler.process.terminate()
    observer.join()
