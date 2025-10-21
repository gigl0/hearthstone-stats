import xml.etree.ElementTree as ET
import json
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
import os
from rich import print  # Per log colorati

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XML_FILE = os.path.join(BASE_DIR, "BgsLastGames.xml")
DATA_DIR = os.path.join(BASE_DIR, "app", "data")

HEROES_JSON = os.path.join(DATA_DIR, "heroes_bg.json")
MINIONS_JSON = os.path.join(DATA_DIR, "minions_bg.json")

# --- Carica mapping eroi e minion ---
# --- Carica mapping eroi e minion ---
def safe_json_load(path):
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


# --- Funzione principale ---
def import_from_hdt_enhanced(xml_path: str = XML_FILE):
    """Importa e pulisce le partite da BgsLastGames.xml, salvandole in PostgreSQL."""
    session = SessionLocal()
    imported = 0

    if not os.path.exists(xml_path):
        print(f"[red]❌ File XML non trovato: {xml_path}[/red]")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for game in root.findall("Game"):
        player_id = game.get("Player")
        hero_id = game.get("Hero")
        placement = int(game.get("Placement") or game.get("Placemenent") or 0)
        start_time = game.get("StartTime")
        end_time = game.get("EndTime")
        rating = int(float(game.get("Rating") or 0))
        rating_after = int(float(game.get("RatingAfter") or 0))

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
                    minions.append({
                        "id": card_id,
                        "name": info.get("name", card_id),
                        "type": info.get("type", ""),
                        "tier": info.get("tier", ""),
                        "image": info.get("image", "")
                    })
                    minion_names.append(info.get("name", card_id))
                    if info.get("type"): minion_types.append(info["type"])
                    if info.get("image"): minion_images.append(info["image"])

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
            minions=json.dumps(minions, ensure_ascii=False)
        )
        session.add(match)
        imported += 1

        print(f"[green]🧩 Match {imported}:[/green] {hero_name} "
              f"({placement}° place, Δ={rating_delta}, {len(minions)} minions)")

    session.commit()
    session.close()

    print(f"[bold green]✅ Import completato: {imported} nuove partite inserite.[/bold green]")
