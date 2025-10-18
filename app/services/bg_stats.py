from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
from datetime import datetime, time
from typing import Optional
import json
from pathlib import Path

# -----------------------------
# CARICA IL JSON DEI MINION
# -----------------------------
MINIONS_JSON = Path("minions_bg.json")
if MINIONS_JSON.exists():
    with open(MINIONS_JSON, encoding="utf-8") as f:
        MINIONS_DICT = json.load(f)
else:
    print(f"[⚠️] File minions_bg.json non trovato. I minion saranno mostrati solo come ID.")
    MINIONS_DICT = {}

# -----------------------------
# STATISTICHE GENERALI
# -----------------------------
def get_bg_stats():
    session = SessionLocal()
    try:
        total_matches = session.query(func.count(BattlegroundsMatch.id)).scalar()
        avg_placement = session.query(func.avg(BattlegroundsMatch.placement)).scalar()
        avg_placement = round(avg_placement, 2) if avg_placement else None

        top_heroes_query = session.query(
            BattlegroundsMatch.hero,
            func.count(BattlegroundsMatch.id).label("wins")
        ).filter(BattlegroundsMatch.placement == 1) \
         .group_by(BattlegroundsMatch.hero) \
         .order_by(func.count(BattlegroundsMatch.id).desc())

        top_heroes = [{"hero": h.hero, "wins": h.wins} for h in top_heroes_query.all()]

        return {
            "total_matches": total_matches,
            "average_placement": avg_placement,
            "top_heroes": top_heroes
        }

    finally:
        session.close()

# -----------------------------
# LISTA PARTITE CON MINION COMPLETI
# -----------------------------
def list_matches(
    limit: int = 20,
    offset: int = 0,
    hero: Optional[str] = None,
    min_placement: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    session = SessionLocal()
    query = session.query(BattlegroundsMatch)

    # Filtri
    if hero:
        query = query.filter(BattlegroundsMatch.hero == hero)
    if min_placement is not None:
        query = query.filter(BattlegroundsMatch.placement <= min_placement)
    if start_date:
        start_dt = datetime.combine(datetime.fromisoformat(start_date), time.min)
        query = query.filter(BattlegroundsMatch.start_time >= start_dt)
    if end_date:
        end_dt = datetime.combine(datetime.fromisoformat(end_date), time.max)
        query = query.filter(BattlegroundsMatch.start_time <= end_dt)

    matches = query.order_by(BattlegroundsMatch.start_time.desc()).offset(offset).limit(limit).all()
    session.close()

    # Trasforma in lista di dict
    result = []
    for m in matches:
        minions_full = []
        for m_id in m.minions.split(";"):
            m_info = MINIONS_DICT.get(m_id)
            if m_info:
                minions_full.append({
                    "id": m_info.get("id", m_id),
                    "name": m_info.get("name", m_id),
                    "type": m_info.get("race",""),
                    "effect": m_info.get("text",""),
                    "image": m_info.get("image",""),
                    "attack": m_info.get("attack",0),
                    "health": m_info.get("health",0)
                })
            else:
                # fallback se il minion non è nel JSON
                minions_full.append({
                    "id": m_id,
                    "name": m_id,
                    "type": "",
                    "effect": "",
                    "image": "",
                    "attack": 0,
                    "health": 0
                })

        result.append({
            "player_id": m.player_id,
            "hero": m.hero,
            "start_time": m.start_time.isoformat(),
            "end_time": m.end_time.isoformat(),
            "placement": m.placement,
            "rating": m.rating,
            "rating_after": m.rating_after,
            "minions": minions_full
        })

    return result
