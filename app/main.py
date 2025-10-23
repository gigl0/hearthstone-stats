# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from datetime import datetime

# === Database setup ===
from app.db.session import engine, SessionLocal
from app.models.models import Base

# === Routers principali ===
from app.routers import matches_router, stats_router, import_router

# --- Crea tabelle se non esistono ---
Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Hearthstone BG Stats API", version="1.3")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in produzione limita ai domini frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers registrati ---
app.include_router(matches_router.router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(stats_router.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(import_router.router, prefix="/api/v1/import", tags=["import"])

# ============================
# ✅ ENDPOINTS DI SERVIZIO
# ============================

@app.get("/")
def root():
    """Root API - verifica che il server sia attivo."""
    return {"message": "🎯 Hearthstone BG API v1.3 attiva"}

@app.get("/api/v1/db/test")
def test_db():
    """Test di connessione al database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        return {
            "status": "ok",
            "engine": str(engine.url).split(":")[0],
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================
# ⚙️ DEBUG: stampa rotte all’avvio
# ============================
print("\n=== ROUTES LOADED ===")
for r in app.routes:
    print(f"{r.path}  -->  {', '.join(r.methods)}")
print("======================\n")
