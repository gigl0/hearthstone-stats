from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Usa SEMPRE la sessione/engine centralizzati
from app.db.session import engine
from app.models.models import Base

# Routers moderni (DB-driven)
from app.routers import matches_router, stats_router

# --- Bootstrap DB: crea le tabelle se non esistono ---
Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Hearthstone BG Stats API", version="1.3")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # se vuoi, restringi a ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers (uniche fonti di verità) ---
app.include_router(matches_router.router)
app.include_router(stats_router.router)

# --- Health & root ---
@app.get("/")
def root():
    return {"message": "Hearthstone BG API v1.3 attiva"}

@app.get("/api/v1/db/test")
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        return {"status": "ok", "engine": str(engine.url).split(':')[0], "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
