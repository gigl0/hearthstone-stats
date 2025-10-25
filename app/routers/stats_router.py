# app/routers/stats_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from app.db.session import get_db
from app.models.models import BattlegroundsMatch

router = APIRouter()

# =========================
# 📊 STATISTICHE GLOBALI
# =========================
@router.get("/global")
def get_global_stats(db: Session = Depends(get_db)):
    total_matches = db.query(func.count(BattlegroundsMatch.id)).scalar()
    if not total_matches:
        return {
            "total_matches": 0,
            "win_rate": 0,
            "top4_rate": 0,
            "avg_placement": 0,
            "avg_duration_min": None,
            "avg_rating_delta": None
        }

    wins = db.query(func.count()).filter(BattlegroundsMatch.game_result == "win").scalar()
    top4 = db.query(func.count()).filter(BattlegroundsMatch.placement <= 4).scalar()
    avg_place = db.query(func.avg(BattlegroundsMatch.placement)).scalar()
    avg_duration = db.query(func.avg(BattlegroundsMatch.duration_min)).scalar()
    avg_rating_delta = db.query(func.avg(BattlegroundsMatch.rating_delta)).scalar()

    return {
        "total_matches": total_matches,
        "win_rate": wins / total_matches,
        "top4_rate": top4 / total_matches,
        "avg_placement": float(avg_place or 0),
        "avg_duration_min": float(avg_duration) if avg_duration is not None else None,
        "avg_rating_delta": float(avg_rating_delta) if avg_rating_delta is not None else None
    }

# =========================
# 🧙‍♂️ STATISTICHE PER EROE
# =========================
@router.get("/heroes")
def get_hero_stats(db: Session = Depends(get_db)):
    """
    Win rate e Top4 rate per eroe.
    """
    results = (
        db.query(
            BattlegroundsMatch.hero_name.label("hero_name"),
            func.avg((BattlegroundsMatch.placement == 1).cast(Integer)).label("win_rate"),
            func.avg((BattlegroundsMatch.placement <= 4).cast(Integer)).label("top4_rate"),
        )
        .filter(BattlegroundsMatch.hero_name.isnot(None))
        .group_by(BattlegroundsMatch.hero_name)
        .all()
    )
    return [
        {"hero": r.hero_name, "win_rate": r.win_rate, "top4_rate": r.top4_rate}
        for r in results
    ]


# =========================
# 🧩 COMPOSIZIONE MINION (placeholder per il PieChart)
# =========================

from fastapi.responses import JSONResponse

@router.get("/minions")
def get_minion_stats(db: Session = Depends(get_db)):
    """
    Top4 rate per tipo di composizione (minion_types).
    """
    results = (
        db.query(
            BattlegroundsMatch.minion_types.label("minion_types"),
            func.avg((BattlegroundsMatch.placement <= 4).cast(Integer)).label("top4_rate"),
        )
        .filter(BattlegroundsMatch.minion_types.isnot(None))
        .group_by(BattlegroundsMatch.minion_types)
        .all()
    )
    return {r.minion_types: {"top4_rate": r.top4_rate} for r in results}


# =========================
# 📈 RATING TREND
# =========================

@router.get("/rating_trend")
def get_rating_trend(db: Session = Depends(get_db)):
    """
    Andamento del rating nel tempo.
    """
    results = (
        db.query(BattlegroundsMatch.end_time, BattlegroundsMatch.rating_after)
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time)
        .all()
    )
    return [
        {"end_time": r.end_time.isoformat(), "rating_after": r.rating_after}
        for r in results
    ]
