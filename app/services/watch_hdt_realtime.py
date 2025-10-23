import os
import time
from datetime import datetime, UTC
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich import print

from app.services.bg_importer_enhanced import import_from_hdt_enhanced
from app.db.session import SessionLocal
from app.models.models import SyncStatus, BattlegroundsMatch, ImportLog

# Percorso del file XML di Hearthstone Deck Tracker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Percorso reale del log di Hearthstone Deck Tracker
XML_PATH = os.path.expandvars(
    r"%APPDATA%\HearthstoneDeckTracker\BgsLastGames.xml"
)



class HDTLogHandler(FileSystemEventHandler):
    """Gestisce gli eventi del file system per il file BgsLastGames.xml."""

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith("BgsLastGames.xml"):
            return

        print(f"[yellow]🕒 File aggiornato: {event.src_path}[/yellow]")
        time.sleep(3)  # attende che HDT termini di scrivere

        try:
            # 🔍 Controlla se ci sono nuove partite
            if not has_new_matches(XML_PATH):
                print("[blue]⏸ Nothing new to import.[/blue]")
                log_import_event(0, "NO_NEW_MATCHES")
                return

            # ✅ Importa nuove partite
            import_from_hdt_enhanced(XML_PATH)
            update_sync_status()
            log_import_event(0, "OK")  # (Il numero esatto dei match è loggato in bg_importer_enhanced)

        except Exception as e:
            print(f"[red]❌ Errore durante l'import automatico: {e}[/red]")
            log_import_event(0, "ERROR")


def has_new_matches(xml_path: str) -> bool:
    """Controlla se il file XML contiene partite più recenti dell’ultima nel DB."""
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_path)
        root = tree.getroot()

        latest_in_xml = max(
            (datetime.fromisoformat(g.get("EndTime").replace("Z", "+00:00"))
             for g in root.findall("Game") if g.get("EndTime")),
            default=None
        )

        if not latest_in_xml:
            return False

        with SessionLocal() as session:
            latest_in_db = session.query(BattlegroundsMatch.end_time).order_by(
                BattlegroundsMatch.end_time.desc()
            ).first()

            if not latest_in_db:
                return True  # DB vuoto → importa tutto

            latest_in_db = latest_in_db[0]
            return latest_in_xml > latest_in_db

    except Exception as e:
        print(f"[red]⚠️ Errore nel controllo nuovi match: {e}[/red]")
        return True  # fallback → tenta comunque l'import


def update_sync_status():
    """Aggiorna la tabella SyncStatus dopo ogni import riuscito."""
    with SessionLocal() as session:
        sync = session.query(SyncStatus).first()
        if not sync:
            sync = SyncStatus(last_import_time=datetime.now(UTC))
            session.add(sync)
        else:
            sync.last_import_time = datetime.now(UTC)
        session.commit()

        print(f"[cyan]🔄 Sync status aggiornato: {sync.last_import_time.isoformat()}[/cyan]")


def log_import_event(matches_imported: int, status: str):
    """Registra ogni evento di import nella tabella import_log."""
    with SessionLocal() as session:
        log_entry = ImportLog(
            matches_imported=matches_imported,
            status=status
        )
        session.add(log_entry)
        session.commit()
        print(f"[cyan]🪵 Import log: {status} ({matches_imported} match)[/cyan]")


def watch_hdt_logs():
    """Avvia il monitoraggio del file BgsLastGames.xml in tempo reale."""
    if not os.path.exists(XML_PATH):
        print(f"[red]❌ File non trovato: {XML_PATH}[/red]")
        return

    event_handler = HDTLogHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(XML_PATH), recursive=False)
    observer.start()

    print(f"[green]👀 Watching {XML_PATH} for changes...[/green]")
    print(f"[blue]Press CTRL+C to stop the watcher.[/blue]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[red]🛑 Watcher interrotto manualmente.[/red]")
    observer.join()


if __name__ == "__main__":
    watch_hdt_logs()
