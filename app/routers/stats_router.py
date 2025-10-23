# app/routers/stats_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    heroes = db.query(BattlegroundsMatch.hero_name).distinct().all()
    if not heroes:
        return []

    hero_stats = []
    for (hero_name,) in heroes:
        hero_matches = (
            db.query(BattlegroundsMatch)
            .filter(BattlegroundsMatch.hero_name == hero_name)
            .all()
        )
        if not hero_matches:
            continue

        total = len(hero_matches)
        wins = sum(1 for m in hero_matches if m.game_result and "win" in m.game_result.lower())
        top4 = sum(1 for m in hero_matches if m.placement and m.placement <= 4)
        avg_place = sum(m.placement for m in hero_matches if m.placement) / total

        hero_stats.append({
            "hero_name": hero_name,
            "matches": total,
            "win_rate": wins / total if total else 0,
            "top4_rate": top4 / total if total else 0,
            "avg_placement": avg_place,
        })

    hero_stats.sort(key=lambda x: x["win_rate"], reverse=True)
    return hero_stats

# =========================
# 🧩 COMPOSIZIONE MINION (placeholder per il PieChart)
# =========================
@router.get("/minions")
def get_minions_placeholder():
    return {
        "Mech": {"games": 10, "top4_rate": 0.7},
        "Beast": {"games": 8, "top4_rate": 0.6},
        "Demon": {"games": 5, "top4_rate": 0.4},
        "Elemental": {"games": 3, "top4_rate": 0.5},
    }

# =========================
# 📈 RATING TREND
# =========================
@router.get("/rating_trend")
def get_rating_trend(db: Session = Depends(get_db)):
    matches = (
        db.query(BattlegroundsMatch.end_time, BattlegroundsMatch.rating_after)
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time.asc())
        .limit(50)
        .all()
    )
    if not matches:
        return []

    return [
        {
            "end_time": m.end_time.isoformat() if m.end_time else None,
            "rating_after": m.rating_after
        }
        for m in matches
    ]
