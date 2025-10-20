from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

app = FastAPI(title="Hearthstone BG Stats API", version="1.0")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oppure ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).parent
DATA_FILE = ROOT.parent / "stats_summary.json"


# === ROUTES ===

@app.get("/")
def root():
    return {"message": "🔥 Hearthstone Battlegrounds Stats API active!"}


@app.get("/api/v1/stats")
def get_all_stats():
    """Restituisce le statistiche globali, per eroe e per minion."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="stats_summary.json non trovato")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@app.get("/api/v1/stats/heroes")
def get_hero_stats():
    """Statistiche per singolo eroe."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="stats_summary.json non trovato")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("by_hero", [])


@app.get("/api/v1/stats/minions")
def get_minion_stats():
    """Statistiche per tipo di minion."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="stats_summary.json non trovato")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("by_minion_type", {})


@app.get("/api/v1/stats/global")
def get_global_stats():
    """Statistiche complessive."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="stats_summary.json non trovato")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("global", {})
