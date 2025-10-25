from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from app.models.models import BattlegroundsMatch

def get_minion_type_stats(db: Session, minion_type: str):
    """
    Calcola winrate, top4 rate, placement medio e rating trend
    per un tipo di composizione specifico (es. NAGA, BEAST, MECH...).
    """

    minion_type = minion_type.strip()
    print("🧠 MINION TYPE REQUESTED:", repr(minion_type))

    # Debug: stampiamo tutti i tipi presenti
    all_types = db.query(BattlegroundsMatch.minion_types).distinct().all()
    print("🧩 MINION TYPES IN DB:", all_types)

    # Query aggregata
    stats = (
        db.query(
            func.count(BattlegroundsMatch.id).label("games_played"),
            func.avg(BattlegroundsMatch.placement).label("avg_placement"),
            func.avg(cast(BattlegroundsMatch.placement == 1, Integer)).label("win_rate"),
            func.avg(cast(BattlegroundsMatch.placement <= 4, Integer)).label("top4_rate"),
            func.avg(BattlegroundsMatch.rating_after).label("avg_rating"),
        )
        .filter(func.lower(BattlegroundsMatch.minion_types) == minion_type.lower())
        .first()
    )

    if not stats or stats.games_played == 0:
        print("⚠️ Nessuna partita trovata per:", minion_type)
        return None

    # Trend rating nel tempo
    trend = (
        db.query(BattlegroundsMatch.end_time, BattlegroundsMatch.rating_after)
        .filter(func.lower(BattlegroundsMatch.minion_types) == minion_type.lower())
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time.asc())
        .all()
    )

    trend_data = [
        {"end_time": t.end_time.isoformat(), "rating_after": t.rating_after}
        for t in trend
    ]

    return {
        "minion_type": minion_type.upper(),
        "games_played": int(stats.games_played or 0),
        "avg_placement": round(stats.avg_placement or 0, 2),
        "win_rate": round(stats.win_rate or 0, 3),
        "top4_rate": round(stats.top4_rate or 0, 3),
        "avg_rating": round(stats.avg_rating or 0, 2),
        "trend": trend_data,
    }
