from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer, case
from app.models.models import BattlegroundsMatch

# ================================
# 🎯 WIN/LOSS STREAKS
# ================================
def get_streaks(db: Session):
    matches = (
        db.query(BattlegroundsMatch.game_result, BattlegroundsMatch.start_time, BattlegroundsMatch.end_time)
        .order_by(BattlegroundsMatch.start_time.asc())
        .all()
    )

    streaks = []
    current = {"result": None, "count": 0, "start": None, "end": None}

    for m in matches:
        if current["result"] is None:
            current.update({"result": m.game_result, "count": 1, "start": m.start_time, "end": m.end_time})
        elif m.game_result == current["result"]:
            current["count"] += 1
            current["end"] = m.end_time
        else:
            streaks.append(current)
            current = {"result": m.game_result, "count": 1, "start": m.start_time, "end": m.end_time}

    if current["result"]:
        streaks.append(current)

    return streaks


# ================================
# 🕒 TIMELINE RATING EVOLUTION
# ================================
def get_timeline(db: Session):
    matches = (
        db.query(
            BattlegroundsMatch.end_time,
            BattlegroundsMatch.rating_after,
            BattlegroundsMatch.rating_delta,
            BattlegroundsMatch.hero_name,
            BattlegroundsMatch.placement,
        )
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time.asc())
        .all()
    )

    data = []
    for m in matches:
        data.append({
            "time": m.end_time.isoformat(),
            "rating": m.rating_after,
            "delta": m.rating_delta,
            "hero": m.hero_name,
            "placement": m.placement
        })
    return data


# ================================
# ⏱️ MATCH DURATION STATS
# ================================
def get_match_duration_stats(db: Session):
    q = db.query(
        func.avg(BattlegroundsMatch.duration_min),
        func.min(BattlegroundsMatch.duration_min),
        func.max(BattlegroundsMatch.duration_min),
    ).first()
    return {
        "avg_duration": round(q[0] or 0, 2),
        "min_duration": round(q[1] or 0, 2),
        "max_duration": round(q[2] or 0, 2),
    }


# ================================
# 📊 DISTRIBUTION OF PLACEMENTS
# ================================
def get_placement_distribution(db: Session):
    results = (
        db.query(BattlegroundsMatch.placement, func.count(BattlegroundsMatch.id))
        .group_by(BattlegroundsMatch.placement)
        .all()
    )
    total = sum(r[1] for r in results)
    return [
        {"placement": r[0], "percentage": round(r[1] / total, 3) if total > 0 else 0}
        for r in results
    ]


# ================================
# 📈 ELO PROGRESSION ESTIMATED
# ================================
def get_elo_progression(db: Session):
    matches = (
        db.query(BattlegroundsMatch.end_time, BattlegroundsMatch.rating_after)
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time.asc())
        .all()
    )

    elo_data = []
    last = None
    for m in matches:
        if last is None:
            diff = 0
        else:
            diff = m.rating_after - last
        last = m.rating_after
        elo_data.append({"time": m.end_time.isoformat(), "rating": m.rating_after, "diff": diff})
    return elo_data
