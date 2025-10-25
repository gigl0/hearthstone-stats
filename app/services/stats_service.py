from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.models import BattlegroundsMatch


def get_summary_stats(db: Session, limit: int = 20):
    """
    Restituisce un riepilogo delle ultime N partite.
    - placement medio
    - winrate / top4 rate
    - durata media
    - variazione media rating
    - eroe più giocato / con winrate migliore
    - composizione più frequente
    """

    # Estrai le ultime N partite
    recent_matches = (
        db.query(BattlegroundsMatch)
        .order_by(desc(BattlegroundsMatch.end_time))
        .limit(limit)
        .all()
    )

    if not recent_matches:
        return {"message": "Nessuna partita trovata nel database."}

    total = len(recent_matches)
    wins = sum(1 for m in recent_matches if m.game_result == "win")
    top4 = sum(1 for m in recent_matches if m.placement and m.placement <= 4)

    avg_placement = sum(m.placement for m in recent_matches if m.placement) / total
    avg_duration = (
        sum(m.duration_min for m in recent_matches if m.duration_min) / total
        if any(m.duration_min for m in recent_matches)
        else None
    )
    avg_rating_delta = (
        sum(m.rating_delta for m in recent_matches if m.rating_delta) / total
        if any(m.rating_delta for m in recent_matches)
        else None
    )

    # Eroe più giocato
    hero_counts = {}
    for m in recent_matches:
        if m.hero_name:
            hero_counts[m.hero_name] = hero_counts.get(m.hero_name, 0) + 1

    most_played_hero = max(hero_counts, key=hero_counts.get) if hero_counts else None

    # Tipo di composizione più frequente
    comp_counts = {}
    for m in recent_matches:
        if m.minion_types:
            comp_counts[m.minion_types] = comp_counts.get(m.minion_types, 0) + 1

    most_played_comp = max(comp_counts, key=comp_counts.get) if comp_counts else None

    # Eroe con winrate migliore
    hero_wins = {}
    for m in recent_matches:
        if m.hero_name:
            if m.hero_name not in hero_wins:
                hero_wins[m.hero_name] = {"wins": 0, "total": 0}
            hero_wins[m.hero_name]["total"] += 1
            if m.game_result == "win":
                hero_wins[m.hero_name]["wins"] += 1

    best_hero = None
    best_rate = 0
    for hero, val in hero_wins.items():
        rate = val["wins"] / val["total"]
        if rate > best_rate:
            best_rate = rate
            best_hero = hero

    return {
        "matches_analyzed": total,
        "win_rate": round(wins / total, 3),
        "top4_rate": round(top4 / total, 3),
        "avg_placement": round(avg_placement, 2),
        "avg_duration_min": round(avg_duration, 2) if avg_duration else None,
        "avg_rating_delta": round(avg_rating_delta, 2) if avg_rating_delta else None,
        "most_played_hero": most_played_hero,
        "most_played_comp": most_played_comp,
        "best_hero": best_hero,
        "best_hero_winrate": round(best_rate, 3) if best_hero else None,
    }
