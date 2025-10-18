import csv
from datetime import datetime
import os
import sys

# Permette di trovare il modulo app anche da scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch

# Percorso assoluto del CSV (root del progetto)
CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parsed_games.csv")

def load_csv_to_db():
    if not os.path.exists(CSV_FILE):
        print(f"[❌] CSV file not found: {CSV_FILE}")
        return

    session = SessionLocal()
    total_added = 0
    total_skipped = 0

    with open(CSV_FILE, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                start_time = datetime.fromisoformat(row['start_time'])
                end_time = datetime.fromisoformat(row['end_time'])
                placement = int(row['placement'])
                rating = int(row['rating'])
                rating_after = int(row['rating_after'])
                player_id = row['player_id']
                hero = row['hero']
                minions = row.get('minions', '')

                # Evita duplicati
                exists = session.query(BattlegroundsMatch).filter(
                    BattlegroundsMatch.player_id == player_id,
                    BattlegroundsMatch.start_time == start_time
                ).first()
                if exists:
                    total_skipped += 1
                    continue

                match = BattlegroundsMatch(
                    player_id=player_id,
                    hero=hero,
                    start_time=start_time,
                    end_time=end_time,
                    placement=placement,
                    rating=rating,
                    rating_after=rating_after,
                    minions=minions
                )
                session.add(match)
                total_added += 1

            except Exception as e:
                print(f"[⚠️] Skipping row due to error: {e}")
                continue

    session.commit()
    session.close()

    print(f"[✅] CSV imported! Added: {total_added}, Skipped (duplicates): {total_skipped}")

if __name__ == "__main__":
    load_csv_to_db()
