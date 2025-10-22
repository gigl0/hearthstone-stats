import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.bg_importer_enhanced import import_from_hdt_enhanced
from rich import print

LOG_DIR = os.path.expanduser(r"~\AppData\Roaming\HearthstoneDeckTracker")
XML_FILE = os.path.join(LOG_DIR, "BgsLastGames.xml")


class HDTLogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if os.path.basename(event.src_path) == "BgsLastGames.xml":
            print(f"\n📜 File aggiornato: {event.src_path}")
        try:
            import_from_hdt_enhanced(XML_FILE)
        except Exception as e:
            print(f"⚠️ Errore durante l'import: {e}")
        else:
            print("✅ Database aggiornato con le ultime partite.\n")


def watch_logs():
    print(f"[bold cyan]👀 In ascolto su {LOG_DIR} per aggiornamenti di HDT...[/bold cyan]")
    event_handler = HDTLogHandler()
    observer = Observer()
    observer.schedule(event_handler, LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[yellow]🛑 Interruzione manuale, watcher fermato.[/yellow]")
    observer.join()

if __name__ == "__main__":
    watch_logs()
