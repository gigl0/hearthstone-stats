from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.advanced_stats_service import (
    get_streaks,
    get_timeline,
    get_match_duration_stats,
    get_placement_distribution,
    get_elo_progression,
)

router = APIRouter()

@router.get("/streaks")
def streaks(db: Session = Depends(get_db)):
    return get_streaks(db)

@router.get("/timeline")
def timeline(db: Session = Depends(get_db)):
    return get_timeline(db)

@router.get("/match_duration")
def match_duration(db: Session = Depends(get_db)):
    return get_match_duration_stats(db)

@router.get("/distribution")
def distribution(db: Session = Depends(get_db)):
    return get_placement_distribution(db)

@router.get("/elo_progression")
def elo_progression(db: Session = Depends(get_db)):
    return get_elo_progression(db)
