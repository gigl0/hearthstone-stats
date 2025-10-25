from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from app.models.models import BattlegroundsMatch


def get_hero_stats_summary(db: Session, hero_name: str):
    hero_name = hero_name.strip()
    print("🧠 HERO REQUESTED:", repr(hero_name))

    heroes = db.query(BattlegroundsMatch.hero_name).distinct().all()
    print("🧩 HEROES IN DB:", heroes)

    result = (
        db.query(
            func.count(BattlegroundsMatch.id).label("games_played"),
            func.avg(BattlegroundsMatch.placement).label("avg_placement"),
            func.avg(cast(BattlegroundsMatch.placement == 1, Integer)).label("win_rate"),
            func.avg(cast(BattlegroundsMatch.placement <= 4, Integer)).label("top4_rate"),
            func.avg(BattlegroundsMatch.rating_after).label("avg_rating"),
        )
        .filter(func.lower(BattlegroundsMatch.hero_name) == hero_name.lower())
        .first()
    )

    if not result or result.games_played == 0:
        print("⚠️ Nessun match trovato per:", hero_name)
        return None

    return {
        "hero": hero_name,
        "games_played": int(result.games_played or 0),
        "avg_placement": float(result.avg_placement or 0),
        "win_rate": float(result.win_rate or 0),
        "top4_rate": float(result.top4_rate or 0),
        "avg_rating": float(result.avg_rating or 0),
    }