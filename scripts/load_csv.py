import csv
from datetime import datetime
import sys
import os

# Permette di trovare il modulo app anche da scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch

CSV_FILE = "parsed_games.csv"  # Assicurati che sia nella root del progetto

def load_csv_to_db():
    session = SessionLocal()

    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Evitiamo duplicati: player_id + start_time
            exists = session.query(BattlegroundsMatch).filter(
                BattlegroundsMatch.player_id == row['player_id'],
                BattlegroundsMatch.start_time == datetime.fromisoformat(row['start_time'])
            ).first()
            if exists:
                continue

            match = BattlegroundsMatch(
                player_id=row['player_id'],
                hero=row['hero'],
                start_time=datetime.fromisoformat(row['start_time']),
                end_time=datetime.fromisoformat(row['end_time']),
                placement=int(row['placement']),
                rating=int(row['rating']),
                rating_after=int(row['rating_after']),
                minions=row['minions']
            )
            session.add(match)

    session.commit()
    session.close()
    print("CSV importato nel database correttamente!")

if __name__ == "__main__":
    load_csv_to_db()
