import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, UTC
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich import print

from app.services.bg_importer_enhanced import import_from_hdt_enhanced
from app.db.session import SessionLocal
from app.models.models import SyncStatus, BattlegroundsMatch, ImportLog


# === Percorso file XML HDT ===
XML_PATH = os.path.expandvars(
    r"%APPDATA%\HearthstoneDeckTracker\BgsLastGames.xml"
)


# ==============================
# 📂 EVENT HANDLER
# ==============================
class HDTLogHandler(FileSystemEventHandler):
    """Gestisce gli eventi di modifica per il file BgsLastGames.xml."""

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith("BgsLastGames.xml"):
            return

        print(f"[yellow]🕒 File aggiornato: {event.src_path}[/yellow]")
        time.sleep(3)  # attende che HDT termini di scrivere il file

        try:
            # 🔍 Controlla se ci sono nuove partite nel file XML
            if not has_new_matches(XML_PATH):
                print("[blue]⏸ Nessuna nuova partita trovata.[/blue]")
                log_import_event(0, "NO_NEW_MATCHES")
                return

            # ✅ Importa le nuove partite
            imported = import_from_hdt_enhanced(XML_PATH)

            # ✅ Aggiorna stato sincronizzazione e log
            update_sync_status()
            log_import_event(imported or 0, "SUCCESS")

        except Exception as e:
            print(f"[red]❌ Errore durante l'import automatico: {e}[/red]")
            log_import_event(0, "ERROR")


# ==============================
# 🧩 FUNZIONI DI SUPPORTO
# ==============================
def has_new_matches(xml_path: str) -> bool:
    """Controlla se il file XML contiene partite più recenti di quelle nel DB."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # trova l'ultimo timestamp nel file XML
        latest_in_xml = max(
            (
                datetime.fromisoformat(g.get("EndTime").replace("Z", "+00:00"))
                for g in root.findall("Game")
                if g.get("EndTime")
            ),
            default=None
        )

        if not latest_in_xml:
            return False

        # confronta con l'ultimo match nel DB
        with SessionLocal() as session:
            latest_in_db = session.query(BattlegroundsMatch.end_time).order_by(
                BattlegroundsMatch.end_time.desc()
            ).first()

            if not latest_in_db or not latest_in_db[0]:
                print("[green]📥 Nessuna partita nel DB — import iniziale.[/green]")
                return True

            latest_in_db = latest_in_db[0]
            is_new = latest_in_xml > latest_in_db

            if is_new:
                print(f"[green]📈 Nuova partita trovata (XML: {latest_in_xml}, DB: {latest_in_db})[/green]")
            else:
                print("[blue]⏸ Nessuna partita più recente trovata.[/blue]")

            return is_new

    except Exception as e:
        print(f"[red]⚠️ Errore nel controllo nuovi match: {e}[/red]")
        return True  # fallback: tenta comunque l'import


def update_sync_status():
    """Aggiorna la tabella SyncStatus dopo ogni import riuscito."""
    with SessionLocal() as session:
        sync = session.query(SyncStatus).first()
        if not sync:
            sync = SyncStatus(last_import_time=datetime.now(UTC), last_status="SUCCESS")
            session.add(sync)
        else:
            sync.last_import_time = datetime.now(UTC)
            sync.last_status = "SUCCESS"
        session.commit()

        print(f"[cyan]🔄 SyncStatus aggiornato: {sync.last_import_time.isoformat()}[/cyan]")


def log_import_event(matches_imported: int, status: str):
    """Registra ogni evento di import nella tabella import_log."""
    with SessionLocal() as session:
        log_entry = ImportLog(
            matches_imported=matches_imported,
            status=status,
            timestamp=datetime.now(UTC)
        )
        session.add(log_entry)
        session.commit()
        print(f"[cyan]🪵 Import log: {status} ({matches_imported} match)[/cyan]")


# ==============================
# 🧠 WATCHER PRINCIPALE
# ==============================
def watch_hdt_logs():
    """Avvia il monitoraggio del file BgsLastGames.xml in tempo reale."""
    if not os.path.exists(XML_PATH):
        print(f"[red]❌ File non trovato: {XML_PATH}[/red]")
        return

    print(f"[green]👀 Watching file: {XML_PATH}[/green]")
    print(f"[blue]Premi CTRL+C per interrompere il watcher.[/blue]")

    event_handler = HDTLogHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(XML_PATH), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[red]🛑 Watcher interrotto manualmente.[/red]")
    observer.join()


if __name__ == "__main__":
    watch_hdt_logs()
