from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.stats_service import get_summary_stats

router = APIRouter()

@router.get("/summary")
def get_summary(limit: int = Query(20, description="Numero di partite da analizzare"), db: Session = Depends(get_db)):
    """
    Riepilogo generale sulle ultime N partite.
    """
    return get_summary_stats(db, limit)
