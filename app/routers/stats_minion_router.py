from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.minion_service import get_minion_type_stats

router = APIRouter()

@router.get("/{minion_type}")
def get_stats_by_minion_type(minion_type: str, db: Session = Depends(get_db)):
    """
    Restituisce statistiche e trend rating per un tipo di composizione (tribù) specifico.
    Esempio: /api/v1/stats/by_minion_type/NAGA
    """
    data = get_minion_type_stats(db, minion_type.upper())
    if not data:
        raise HTTPException(status_code=404, detail=f"Nessuna partita trovata per la composizione '{minion_type}'.")
    return data
