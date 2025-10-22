from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
from datetime import datetime

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/heroes")
def get_hero_stats(db: Session = Depends(get_db)):
    """
    Restituisce statistiche per ogni eroe:
    - numero partite
    - placement medio
    - rating medio
    """
    results = (
        db.query(
            BattlegroundsMatch.hero,
            func.count().label("num_matches"),
            func.avg(BattlegroundsMatch.placement).label("avg_placement"),
            func.avg(BattlegroundsMatch.rating_after).label("avg_rating"),
        )
        .group_by(BattlegroundsMatch.hero)
        .order_by(func.count().desc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="Nessuna statistica trovata")

    heroes = [
        {
            "hero": r.hero,
            "num_matches": r.num_matches,
            "avg_placement": round(r.avg_placement, 2) if r.avg_placement else None,
            "avg_rating": round(r.avg_rating, 2) if r.avg_rating else None,
        }
        for r in results
    ]

    return {"heroes": heroes}


@router.get("/global")
def get_global_stats(db: Session = Depends(get_db)):
    """
    Statistiche globali di tutte le partite:
    - numero totale partite
    - placement medio
    - rating medio
    """
    total_matches = db.query(func.count(BattlegroundsMatch.id)).scalar()
    avg_placement = db.query(func.avg(BattlegroundsMatch.placement)).scalar()
    avg_rating = db.query(func.avg(BattlegroundsMatch.rating_after)).scalar()

    if total_matches == 0:
        raise HTTPException(status_code=404, detail="Nessuna partita nel database")

    return {
        "total_matches": total_matches,
        "avg_placement": round(avg_placement, 2) if avg_placement else None,
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
    }

@router.get("/trend")
def get_rating_trend(limit: int = 50, db: Session = Depends(get_db)):
    """
    Restituisce l'andamento del rating nel tempo (ultime N partite).
    Usato per il grafico della dashboard.
    """
    matches = (
        db.query(
            BattlegroundsMatch.end_time,
            BattlegroundsMatch.rating_after
        )
        .order_by(BattlegroundsMatch.end_time.desc())
        .filter(BattlegroundsMatch.rating_after.isnot(None))
        .order_by(BattlegroundsMatch.end_time.asc())
        .limit(limit)
        .all()
    )

    if not matches:
        raise HTTPException(status_code=404, detail="Nessun dato di rating trovato")

    trend_data = []
    for m in matches:
                end_time = m.end_time
                if isinstance(end_time, str):
                    try:
                        end_time = datetime.fromisoformat(end_time)
                    except Exception:
                        pass  # lascia la stringa se non è in formato ISO

    trend_data.append({
            "end_time": end_time.isoformat() if hasattr(end_time, "isoformat") else str(end_time),
            "rating_after": m.rating_after
        })

    return {"trend": trend_data}
    
