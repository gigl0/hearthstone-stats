# app/routers/stats_hero_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.hero_service import get_hero_stats_summary

router = APIRouter()

@router.get("/by_hero/{hero_name}")
def get_stats_by_hero(hero_name: str, db: Session = Depends(get_db)):
    print("🧠 HERO ENDPOINT CALLED:", hero_name)
    data = get_hero_stats_summary(db, hero_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Nessuna partita trovata per {hero_name}")
    return data
