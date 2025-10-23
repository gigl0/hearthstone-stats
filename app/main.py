from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from datetime import datetime

# Usa la sessione e l’engine centralizzati
from app.db.session import engine, SessionLocal
from app.models.models import Base, SyncStatus

# Routers principali (DB-driven)
from app.routers import matches_router, stats_router
from app.routers import matches_router, stats_router, import_router

# --- Bootstrap DB: crea le tabelle se non esistono ---
Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Hearthstone BG Stats API", version="1.3")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(matches_router.router)
app.include_router(stats_router.router)
app.include_router(matches_router.router)
app.include_router(stats_router.router)
app.include_router(import_router.router)


# --- Root ---
@app.get("/")
def root():
    return {"message": "Hearthstone BG API v1.3 attiva"}


# --- Test connessione DB ---
@app.get("/api/v1/db/test")
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        return {"status": "ok", "engine": str(engine.url).split(':')[0], "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Nuovo endpoint: stato della sincronizzazione ---
@app.get("/api/v1/sync/status")
def get_sync_status():
    """Restituisce l’orario dell’ultima importazione dal file HDT (BgsLastGames.xml)."""
    try:
        with SessionLocal() as session:
            sync = session.query(SyncStatus).first()
            if not sync or not sync.last_import_time:
                return {"last_import_time": None, "status": "no_sync_yet"}
            
            # Calcolo opzionale del tempo trascorso
            diff = datetime.utcnow() - sync.last_import_time
            minutes = round(diff.total_seconds() / 60, 1)

            return {
                "last_import_time": sync.last_import_time.isoformat(),
                "minutes_since": minutes,
                "status": "ok" if minutes < 30 else "stale"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import inspect
print("=== ROUTES LOADED ===")
for r in app.routes:
    print(r.path)
print("======================")
