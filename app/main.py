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

# Funzione loop per aggiornamento CSV ogni ora
def auto_update_csv(interval_sec: int = 360):
    while True:
        try:
            load_csv_to_db()
        except Exception as e:
            print(f"Errore aggiornamento automatico CSV: {e}")
        time.sleep(interval_sec)

# Avvia il thread in background
thread = Thread(target=auto_update_csv, args=(360,), daemon=True)
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
    end_date: Optional[str] = Query(None, description="Filtra per data fine (YYYY-MM-DD)"),
    sort_by: str = Query("start_time", description="Campo per ordinare: start_time, placement, rating"),
    order: str = Query("desc", description="asc o desc")
):
    matches = list_matches()

    # Filtri
    if hero:
        matches = [m for m in matches if m["hero"] == hero]
    if min_placement is not None:
        matches = [m for m in matches if m["placement"] <= min_placement]
    if start_date:
        matches = [m for m in matches if m["start_time"][:10] >= start_date]
    if end_date:
        matches = [m for m in matches if m["start_time"][:10] <= end_date]

    # Ordinamento
    reverse = True if order.lower() == "desc" else False
    matches.sort(key=lambda m: m.get(sort_by, ""), reverse=reverse)

    return matches[offset:offset+limit]
