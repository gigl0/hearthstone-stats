from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
from datetime import datetime, time
from typing import Optional

def get_bg_stats():
    session = SessionLocal()
    
    total_games = session.query(func.count(BattlegroundsMatch.id)).scalar()
    wins = session.query(func.count(BattlegroundsMatch.id)).filter(BattlegroundsMatch.placement == 1).scalar()
    avg_placement = session.query(func.avg(BattlegroundsMatch.placement)).scalar()
    
    hero_counts = session.query(
        BattlegroundsMatch.hero, func.count(BattlegroundsMatch.hero)
    ).group_by(BattlegroundsMatch.hero).all()
    
    session.close()
    
    return {
        "total_games": total_games,
        "wins": wins,
        "winrate": round(wins/total_games*100,2) if total_games else 0,
        "avg_placement": round(avg_placement,2) if avg_placement else 0,
        "hero_counts": {hero: count for hero, count in hero_counts}
    }

def list_matches(limit=20, offset=0):
    session = SessionLocal()
    matches = session.query(BattlegroundsMatch).order_by(BattlegroundsMatch.start_time.desc()).offset(offset).limit(limit).all()
    session.close()
    return [
        {
            "player_id": m.player_id,
            "hero": m.hero,
            "start_time": m.start_time.isoformat(),
            "end_time": m.end_time.isoformat(),
            "placement": m.placement,
            "rating": m.rating,
            "rating_after": m.rating_after,
            "minions": m.minions.split(";")  # lista di minions
        }
        for m in matches
    ]

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

    # -----------------------------
    # APPLICA I FILTRI
    # -----------------------------
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

    # -----------------------------
    # Ordina e limita
    # -----------------------------
    matches = query.order_by(BattlegroundsMatch.start_time.desc()).offset(offset).limit(limit).all()
    session.close()

    # Trasforma in lista di dict per JSON
    return [
        {
            "player_id": m.player_id,
            "hero": m.hero,
            "start_time": m.start_time.isoformat(),
            "end_time": m.end_time.isoformat(),
            "placement": m.placement,
            "rating": m.rating,
            "rating_after": m.rating_after,
            "minions": m.minions.split(";")
        }
        for m in matches
    ]