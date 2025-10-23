from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import BattlegroundsMatch

router = APIRouter(tags=["matches"])


@router.get("/recent")
def get_recent_matches(limit: int = 10, db: Session = Depends(get_db)):
    """
    ✅ Restituisce le ultime partite registrate nel database,
    ordinate per data di fine (end_time) discendente.
    """
    matches = (
        db.query(BattlegroundsMatch)
        .order_by(BattlegroundsMatch.end_time.desc())
        .limit(limit)
        .all()
    )

    # Non solleva errore: ritorna lista vuota se non ci sono partite
    return {"matches": matches}
