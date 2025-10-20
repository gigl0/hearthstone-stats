import time
import os
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = os.path.expanduser(r"~\AppData\Roaming\HearthstoneDeckTracker\Logs")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "matches.csv")

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".log"):
            return
        print(f"📜 Log updated: {event.src_path}")
        update_csv_from_log(event.src_path)

def update_csv_from_log(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Example parsing — customize this for your HDT log format
    new_rows = []
    for line in lines:
        if "Match:" in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                timestamp = parts[0]
                result = parts[-1]
                new_rows.append([timestamp, result])

    if not new_rows:
        return

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in new_rows:
            writer.writerow(row)
    print(f"✅ CSV updated with {len(new_rows)} new rows.")

if __name__ == "__main__":
    print(f"👀 Watching {LOG_DIR} for changes...")
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
