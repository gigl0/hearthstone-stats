import csv
import json
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
import os

CSV_FILE = "parsed_games.csv"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MINIONS_JSON = os.path.join(BASE_DIR, "minions_bg.json")

# Carica il JSON dei minion
with open(MINIONS_JSON, encoding="utf-8") as f:
    MINIONS = json.load(f)

def load_csv_to_db():
    """Popola il DB dalle partite HDT e arricchisce i minion con dati dal JSON."""
    session = SessionLocal()

    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                exists = session.query(BattlegroundsMatch).filter(
                    BattlegroundsMatch.player_id == row['player_id'],
                    BattlegroundsMatch.start_time == datetime.fromisoformat(row['start_time'])
                ).first()
                if exists:
                    continue

                minion_ids = row['minions'].split(";")
                minion_details = []
                for m in minion_ids:
                    details = MINIONS.get(m)
                    if details:
                        minion_details.append(details)
                    else:
                        minion_details.append({"id": m, "name": m, "type": "", "effect": "", "image": ""})

                match = BattlegroundsMatch(
                    player_id=row['player_id'],
                    hero=row['hero'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']),
                    placement=int(row['placement']),
                    rating=int(row['rating']),
                    rating_after=int(row['rating_after']),
                    minions=json.dumps(minion_details)
                )
                session.add(match)

        session.commit()
        print(f"[✅] CSV importato nel database correttamente ({CSV_FILE})!")
    except FileNotFoundError:
        print(f"[❌] File CSV non trovato: {CSV_FILE}")
    except Exception as e:
        print(f"[❌] Errore durante l'import CSV: {e}")
    finally:
        session.close()


def get_all_matches():
    """Restituisce tutte le partite dal DB con minion già arricchiti come oggetti Python."""
    session = SessionLocal()
    try:
        matches = session.query(BattlegroundsMatch).all()
        result = []
        for m in matches:
            result.append({
                "player_id": m.player_id,
                "hero": m.hero,
                "start_time": m.start_time.isoformat(),
                "end_time": m.end_time.isoformat(),
                "placement": m.placement,
                "rating": m.rating,
                "rating_after": m.rating_after,
                "minions": json.loads(m.minions)  # qui i minion sono già oggetti con stats e immagini
            })
        return result
    finally:
        session.close()
