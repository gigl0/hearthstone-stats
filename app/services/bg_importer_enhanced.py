import xml.etree.ElementTree as ET
import json
from datetime import datetime, UTC
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch, SyncStatus, ImportLog
import os
import time
from rich import print  # Log colorati eleganti


# === Percorsi ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XML_FILE = os.path.expandvars(r"%APPDATA%\HearthstoneDeckTracker\BgsLastGames.xml")
DATA_DIR = os.path.join(BASE_DIR, "app", "data")

HEROES_JSON = os.path.join(DATA_DIR, "heroes_bg.json")
MINIONS_JSON = os.path.join(DATA_DIR, "minions_bg.json")


# === Funzioni di supporto ===
def safe_json_load(path):
    """Tenta più codifiche per leggere file JSON in modo robusto."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"❌ Impossibile leggere {path} in nessuna codifica supportata.")


try:
    HERO_DATA = safe_json_load(HEROES_JSON)
    MINION_DATA = safe_json_load(MINIONS_JSON)
    print(f"[cyan]✅ Loaded {len(HERO_DATA)} heroes and {len(MINION_DATA)} minions mappings.[/cyan]")
except Exception as e:
    HERO_DATA, MINION_DATA = {}, {}
    print(f"[red]⚠️ Errore nel caricamento dei mapping: {e}[/red]")


# === Funzione principale ===
def import_from_hdt_enhanced(xml_path: str = XML_FILE):
    """Importa e pulisce le partite da BgsLastGames.xml, salvandole in PostgreSQL."""
    session = SessionLocal()
    imported = 0

    if not os.path.exists(xml_path):
        print(f"[red]❌ File XML non trovato: {xml_path}[/red]")
        _log_import(session, 0, "ERROR")
        session.close()
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[red]❌ Errore nel parsing XML: {e}[/red]")
        _log_import(session, 0, "ERROR")
        session.close()
        return

    try:
        for game in root.findall("Game"):
            player_id = game.get("Player")
            hero_id = game.get("Hero")
            start_time = game.get("StartTime")
            end_time = game.get("EndTime")
            rating = int(float(game.get("Rating") or 0))
            rating_after = int(float(game.get("RatingAfter") or 0))

            # === FIX typo 'Placemenent' + retry 3x ===
            def _get_placement(node):
                s = (
                    node.get("Placement")
                    or node.get("Placemenent")
                    or node.get("FinalPlacement")
                )
                return int(s) if s and s.isdigit() else 0

            placement = _get_placement(game)

            retry_count = 0
            while (placement == 0 or placement > 8) and retry_count < 3:
                print(f"[yellow]⏳ Placement mancante, ritento tra 3s... ({retry_count+1}/3)[/yellow]")
                time.sleep(3)
                try:
                    tree_retry = ET.parse(xml_path)
                    root_retry = tree_retry.getroot()
                    game_retry = next(
                        (g for g in root_retry.findall("Game") if g.get("StartTime") == start_time),
                        None
                    )
                    if game_retry:
                        placement = _get_placement(game_retry)
                except Exception:
                    pass
                retry_count += 1

            # Se ancora non trovato → skip
            if placement <= 0 or placement > 8:
                print(f"[magenta]⏸ Skippato {hero_id or 'UNKNOWN'}: placement ancora mancante dopo {retry_count} tentativi.[/magenta]")
                continue

            # --- Evita duplicati ---
            exists = session.query(BattlegroundsMatch).filter_by(
                player_id=player_id,
                start_time=datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            ).first()
            if exists:
                continue

            # --- HERO INFO ---
            hero_info = HERO_DATA.get(hero_id, {"name": hero_id, "image": ""})
            hero_name = hero_info.get("name", hero_id)
            hero_image = hero_info.get("image", "")

            # --- MINIONS ---
            final_board = game.find("FinalBoard")
            minions, minion_names, minion_types, minion_images = [], [], [], []
            if final_board is not None:
                for m in final_board.findall("Minion"):
                    card_node = m.find("CardId")
                    if card_node is not None and card_node.text:
                        card_id = card_node.text.strip().upper().replace("_G", "")
                        info = MINION_DATA.get(card_id, {})
                        minion_data = {
                            "id": card_id,
                            "name": info.get("name", card_id),
                            "type": info.get("type", ""),
                            "tier": info.get("tier", ""),
                            "image": info.get("image", "")
                        }
                        minions.append(minion_data)
                        minion_names.append(minion_data["name"])
                        if minion_data["type"]:
                            minion_types.append(minion_data["type"])
                        if minion_data["image"]:
                            minion_images.append(minion_data["image"])

            # --- METRICHE DERIVATE ---
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                duration_min = round((end_dt - start_dt).total_seconds() / 60, 1)
            except Exception:
                duration_min = None

            rating_delta = rating_after - rating
            if placement == 1:
                game_result = "win"
            elif 2 <= placement <= 4:
                game_result = "top4"
            else:
                game_result = "loss"

            # --- Inserisci nel DB ---
            match = BattlegroundsMatch(
                player_id=player_id,
                hero=hero_id,
                start_time=start_dt,
                end_time=end_dt,
                placement=placement,
                rating=rating,
                rating_after=rating_after,
                minions=minions,
                hero_name=hero_name,
                hero_image=hero_image,
                duration_min=duration_min,
                rating_delta=rating_delta,
                game_result=game_result,
                minions_count=len(minions),
                minions_list=", ".join(minion_names),
                minion_types=", ".join(sorted(set(minion_types))),
                minion_images="|".join(minion_images)
            )
            session.add(match)
            imported += 1

            print(f"[green]🧩 Match {imported}:[/green] {hero_name} ({placement}° place, Δ={rating_delta}, {len(minions)} minions)")

        # --- Aggiorna SyncStatus ---
        sync = session.query(SyncStatus).first()
        if not sync:
            sync = SyncStatus(last_import_time=datetime.now(UTC))
            session.add(sync)
        else:
            sync.last_import_time = datetime.now(UTC)

        session.commit()

        # --- Log Import ---
        status = "OK" if imported > 0 else "NO_NEW_MATCHES"
        _log_import(session, imported, status)

        print(f"[bold green]✅ Import completato: {imported} nuove partite inserite.[/bold green]")

    except Exception as e:
        session.rollback()
        print(f"[red]❌ Errore durante l'import: {e}[/red]")
        _log_import(session, 0, "ERROR")

    finally:
        session.close()


# === Utility interna per registrare log import ===
def _log_import(session, matches_imported: int, status: str):
    try:
        log_entry = ImportLog(matches_imported=matches_imported, status=status)
        session.add(log_entry)
        session.commit()
        print(f"[cyan]🪵 Import log registrato: {matches_imported} match - {status}[/cyan]")
    except Exception as e:
        session.rollback()
        print(f"[red]⚠️ Errore nel salvataggio import log: {e}[/red]")
