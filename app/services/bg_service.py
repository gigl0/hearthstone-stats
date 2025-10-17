import csv
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch

CSV_FILE = "parsed_games.csv"  # Deve essere nella root del progetto

def load_csv_to_db():
    """
    Legge il CSV delle partite di Battlegrounds e le inserisce nel DB SQLite.
    Evita di inserire duplicati.
    """
    session = SessionLocal()

    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Evita duplicati: player_id + start_time
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
        print(f"CSV importato nel database correttamente ({CSV_FILE})!")

    except FileNotFoundError:
        print(f"File CSV non trovato: {CSV_FILE}")
    except Exception as e:
        print(f"Errore durante l'import CSV: {e}")
    finally:
        session.close()
