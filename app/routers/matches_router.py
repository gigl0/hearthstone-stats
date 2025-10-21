from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recent")
def get_recent_matches(limit: int = 10, db: Session = Depends(get_db)):
    """Restituisce le ultime partite dal database."""
    matches = (
        db.query(BattlegroundsMatch)
        .order_by(BattlegroundsMatch.end_time.desc())
        .limit(limit)
        .all()
    )
    if not matches:
        raise HTTPException(status_code=404, detail="Nessuna partita trovata nel database")
    return matches
