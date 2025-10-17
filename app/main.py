from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from typing import Optional
from threading import Thread
import time
from app.services.bg_service import load_csv_to_db
from app.services.bg_stats import get_bg_stats, list_matches

app = FastAPI(title="Hearthstone Battlegrounds Stats")

# Servire file statici per il frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Funzione loop per aggiornamento CSV
def auto_update_csv(interval_sec: int = 3600):
    while True:
        try:
            load_csv_to_db()
        except Exception as e:
            print(f"Errore aggiornamento automatico CSV: {e}")
        time.sleep(interval_sec)

# Avvia il thread in background
thread = Thread(target=auto_update_csv, args=(3600,), daemon=True)
thread.start()

@app.get("/api/v1/bg/stats")
def bg_stats():
    return get_bg_stats()

@app.get("/api/v1/bg/matches")
def bg_matches(
    limit: int = 20,
    offset: int = 0,
    hero: Optional[str] = Query(None, description="Filtra per eroe"),
    min_placement: Optional[int] = Query(None, description="Filtra per posizionamento massimo"),
    start_date: Optional[str] = Query(None, description="Filtra per data inizio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filtra per data fine (YYYY-MM-DD)")
):
    return list_matches(limit=limit, offset=offset, hero=hero, min_placement=min_placement, start_date=start_date, end_date=end_date)