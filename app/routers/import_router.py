# app/routers/import_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db, SessionLocal
from app.models.models import ImportLog, SyncStatus
import os
import time

router = APIRouter()

# ================================
# 🧩 Endpoint: stato sincronizzazione
# ================================
@router.get("/status")
def get_sync_status(db: Session = Depends(get_db)):
    """Restituisce l'orario dell'ultima importazione e lo stato corrente."""
    sync = db.query(SyncStatus).first()
    if not sync:
        return {"last_import_time": None, "last_status": "no_sync_yet"}

    diff = datetime.utcnow() - sync.last_import_time if sync.last_import_time else None
    minutes = round(diff.total_seconds() / 60, 1) if diff else None

    return {
        "last_import_time": sync.last_import_time.isoformat() if sync.last_import_time else None,
        "minutes_since": minutes,
        "last_status": sync.last_status or "unknown",
    }

# ================================
# 🧾 Endpoint: log importazioni
# ================================
@router.get("/logs")
def get_import_logs(db: Session = Depends(get_db)):
    """Restituisce la lista dei log di import (più recenti per primi)."""
    logs = db.query(ImportLog).order_by(ImportLog.timestamp.desc()).limit(20).all()
    if not logs:
        return []
    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "matches_imported": log.matches_imported,
            "status": log.status,
        }
        for log in logs
    ]

# ================================
# ▶️ Endpoint: avvio manuale importazione
# ================================
@router.post("/start")
def trigger_import(db: Session = Depends(get_db)):
    """
    Avvia manualmente l'importazione da file (mock).
    In futuro: qui si potrà integrare la logica del parser XML BgsLastGames.xml.
    """
    try:
        # 🔸 Simulazione importazione
        matches_imported = 5
        time.sleep(1.5)

        # 🔸 Aggiorna SyncStatus
        sync = db.query(SyncStatus).first()
        if not sync:
            sync = SyncStatus()
            db.add(sync)
        sync.last_import_time = datetime.utcnow()
        sync.last_status = "SUCCESS"

        # 🔸 Registra nel log
        new_log = ImportLog(
            timestamp=datetime.utcnow(),
            matches_imported=matches_imported,
            status="SUCCESS",
        )
        db.add(new_log)
        db.commit()

        return {"message": "Importazione completata", "matches_imported": matches_imported}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante l'import: {str(e)}")
