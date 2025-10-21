# parse_hdt_bg.py aggiornato
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
import xml.etree.ElementTree as ET
from datetime import datetime

def import_from_hdt(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    session = SessionLocal()

    for game in root.findall("Game"):
        placement = game.get("Placement") or game.get("Placemenent")
        match = BattlegroundsMatch(
            player_id=game.get("Player"),
            hero=game.get("Hero"),
            start_time=datetime.fromisoformat(game.get("StartTime")),
            end_time=datetime.fromisoformat(game.get("EndTime")),
            placement=int(placement or 0),
            rating=int(game.get("Rating") or 0),
            rating_after=int(game.get("RatingAfter") or 0),
            minions=""
        )
        session.add(match)
    session.commit()
    session.close()
