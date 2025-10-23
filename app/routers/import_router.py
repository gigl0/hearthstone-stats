from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import ImportLog
from app.services.bg_importer_enhanced import import_from_hdt_enhanced
from rich import print

router = APIRouter(prefix="/api/v1/import", tags=["Import Logs & Control"])


@router.get("/logs")
def get_import_logs(limit: int = 20):
    """Restituisce gli ultimi eventi di import registrati."""
    try:
        session: Session = SessionLocal()
        logs = (
            session.query(ImportLog)
            .order_by(ImportLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        session.close()

        return [
            {
                "timestamp": log.timestamp.isoformat(),
                "matches_imported": log.matches_imported,
                "status": log.status,
            }
            for log in logs
        ]

    except Exception as e:
        print(f"[red]⚠️ Errore durante la lettura dei log: {e}[/red]")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
def run_import_now():
    """Esegue manualmente l'importazione dei match da HDT."""
    try:
        import_from_hdt_enhanced()
        return {"status": "ok", "message": "Import eseguito con successo"}
    except Exception as e:
        print(f"[red]❌ Errore durante l'import manuale: {e}[/red]")
        raise HTTPException(status_code=500, detail=str(e))
