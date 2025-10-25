# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.session import engine
from app.models.models import Base
from app.routers import matches_router, stats_router, import_router
from app.routers import stats_hero_router, stats_minion_router, stats_basic_router, stats_advanced_router

from dotenv import load_dotenv
import os
# --- Crea tabelle se non esistono ---
Base.metadata.create_all(bind=engine)

# --- App FastAPI ---
app = FastAPI(title="Hearthstone BG Stats API", version="1.3")

# --- CORS per React in dev (porta 3000) ---
load_dotenv()

origins = [os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers registrati ---
app.include_router(matches_router.router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(stats_router.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(import_router.router, prefix="/api/v1/import", tags=["import"])
app.include_router(stats_hero_router.router, prefix="/api/v1/stats", tags=["stats-hero"])
app.include_router(stats_minion_router.router, prefix="/api/v1/stats/by_minion_type", tags=["stats-minion"])
app.include_router(stats_basic_router.router, prefix="/api/v1/stats", tags=["stats-basic"])
app.include_router(stats_advanced_router.router, prefix="/api/v1/stats", tags=["stats-advanced"])
# --- Endpoint di test ---
@app.get("/")
def root():
    """Verifica che il backend sia attivo"""
    return {"message": "🎯 Hearthstone BG API (dev mode)"}

@app.get("/api/v1/db/test")
def test_db():
    """Test di connessione al database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Debug: stampa rotte caricate ---
print("\n=== ROUTES LOADED ===")
for r in app.routes:
    if hasattr(r, "methods"):
        print(f"{r.path}  -->  {', '.join(r.methods)}")
