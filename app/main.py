from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import pandas as pd
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"
MINIONS_FILE = DATA_DIR / "minions_bg.json"

app = FastAPI(title="Hearthstone BG Stats API", version="1.0")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oppure ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve la cartella /app/data come contenuti statici
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


# === PATH ===
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "stats_summary.json"
CSV_FILE = DATA_DIR / "parsed_games_clean.csv"
MINIONS_FILE = DATA_DIR / "minions_bg.json"

# === Carica mappa minion una sola volta ===
try:
    with open(MINIONS_FILE, "r", encoding="utf-8") as f:
        minions_data = json.load(f)
    MINION_MAP = {mid.upper(): info.get("name", mid) for mid, info in minions_data.items()}
except Exception as e:
    print(f"⚠️ Errore nel caricamento di minions_bg.json: {e}")
    MINION_MAP = {}

# === ROUTES ===

@app.get("/")
def root():
    return {"message": "Hearthstone Battlegrounds Stats API active!"}


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


@app.get("/api/v1/stats/rating_trend")
def get_rating_trend():
    """Andamento del rating nel tempo."""
    if not CSV_FILE.exists():
        raise HTTPException(status_code=404, detail="parsed_games_clean.csv non trovato")
    df = pd.read_csv(CSV_FILE)
    trend = df[["end_time", "rating_after"]].dropna().sort_values("end_time")
    data = [
        {"end_time": row["end_time"], "rating_after": int(row["rating_after"])}
        for _, row in trend.iterrows()
    ]
    return data


# === NUOVO ENDPOINT ===
@app.get("/api/v1/matches/recent")
def get_recent_matches(limit: int = 10):
    """Ultime partite con dettagli eroe e minion (nomi e immagini)."""
    if not CSV_FILE.exists():
        raise HTTPException(status_code=404, detail="parsed_games_clean.csv non trovato")

    df = pd.read_csv(CSV_FILE)
    df = df.sort_values("end_time", ascending=False).head(limit)

    matches = []
    for _, row in df.iterrows():
        raw_minions = str(row.get("minions_list", "")).split(";")
        raw_images = (
                        str(row.get("minion_images", ""))
                        .replace("||", ";")
                        .replace("|", ";")
                        .replace("\\\\", "\\")
                        .split(";")
                    )
        raw_images = [img.strip() for img in raw_images if img.strip()]



        # Converte i codici in nomi leggibili
        minion_names = []
        for mid in raw_minions:
            clean_id = mid.replace("_G", "").strip().upper()
            name = MINION_MAP.get(clean_id, clean_id)
            if name:
                minion_names.append(name)

        matches.append({
            "hero_name": row.get("hero_name", ""),
            "hero_image": row.get("hero_image", ""),
            "placement": int(row.get("placement", 0)),
            "game_result": row.get("game_result", ""),
            "rating_after": int(row.get("rating_after", 0)),
            "rating_delta": int(row.get("rating_delta", 0)),
            "duration_min": round(float(row.get("duration_min", 0)), 1),
            "end_time": row.get("end_time", ""),
            "minions_list": minion_names,
            "minion_images": [img for img in raw_images if img],
        })

    return {"matches": matches}
