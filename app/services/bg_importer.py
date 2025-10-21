import xml.etree.ElementTree as ET
import json
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XML_FILE = os.path.join(BASE_DIR, "BgsLastGames.xml")
MINIONS_JSON = os.path.join(BASE_DIR, "app", "data", "minions_bg.json")

# Carica i dati dei minion (id -> info)
try:
    with open(MINIONS_JSON, encoding="utf-8") as f:
        MINION_DATA = json.load(f)
except FileNotFoundError:
    MINION_DATA = {}
    print("⚠️ File minions_bg.json non trovato, i dettagli dei minion saranno vuoti.")

def import_from_hdt(xml_path: str = XML_FILE):
    """Importa partite da BgsLastGames.xml in PostgreSQL, con minion arricchiti da minions_bg.json."""
    session = SessionLocal()
    tree = ET.parse(xml_path)
    root = tree.getroot()
    imported = 0

    for game in root.findall("Game"):
        player_id = game.get("Player")
        hero = game.get("Hero")
        placement = game.get("Placement") or game.get("Placemenent")
        start_time = game.get("StartTime")
        end_time = game.get("EndTime")
        rating = game.get("Rating")
        rating_after = game.get("RatingAfter")

        # Evita duplicati
        exists = session.query(BattlegroundsMatch).filter_by(
            player_id=player_id,
            start_time=datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        ).first()
        if exists:
            continue

        # --- Lettura minion dal FinalBoard ---
        minions = []
        final_board = game.find("FinalBoard")
        if final_board is not None:
            for m in final_board.findall("Minion"):
                card_node = m.find("CardId")
                if card_node is not None and card_node.text:
                    card_id = card_node.text.strip().upper()
                    info = MINION_DATA.get(card_id, {})
                    minions.append({
                        "id": card_id,
                        "name": info.get("name", card_id),
                        "type": info.get("type", ""),
                        "tier": info.get("tier", ""),
                        "image": info.get("image", "")
                    })

        # --- Inserimento nel DB ---
        match = BattlegroundsMatch(
            player_id=player_id,
            hero=hero,
            start_time=datetime.fromisoformat(start_time.replace("Z", "+00:00")),
            end_time=datetime.fromisoformat(end_time.replace("Z", "+00:00")),
            placement=int(placement or 0),
            rating=int(float(rating or 0)),
            rating_after=int(float(rating_after or 0)),
            minions=json.dumps(minions, ensure_ascii=False)
        )
        session.add(match)
        imported += 1

        print(f"🧩 Match {imported} ({hero}) – {len(minions)} minion importati")

    session.commit()
    session.close()
    print(f"✅ Import completato: {imported} partite inserite con minion dettagliati.")
