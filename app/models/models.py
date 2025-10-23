from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime, UTC
class BattlegroundsMatch(Base):
    __tablename__ = "battlegrounds_matches"

    # --- Identificatori base ---
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    hero = Column(String)
    
    # --- Info temporali ---
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    # --- Risultati di gioco ---
    placement = Column(Integer)
    rating = Column(Integer)
    rating_after = Column(Integer)

    # --- Dati “grezzi” ---
    minions = Column(JSONB)  # ✅ PostgreSQL usa jsonb per oggetti JSON
    # (se vuoi compatibilità cross-db, usa Column(JSON), ma qui è meglio JSONB)

    # --- Dati derivati / puliti ---
    hero_name = Column(String)
    hero_image = Column(String)
    duration_min = Column(Float)
    rating_delta = Column(Integer)
    game_result = Column(String)  # "win", "top4", "loss"

    # --- Dati minion arricchiti ---
    minions_count = Column(Integer)
    minions_list = Column(String)       # lista dei nomi, separati da virgole
    minion_types = Column(String)       # tipi unici separati da virgole
    minion_images = Column(String)      # link uniti da "|"

    def __repr__(self):
        return (f"<BattlegroundsMatch(id={self.id}, hero={self.hero_name}, "
                f"placement={self.placement}, rating_delta={self.rating_delta})>")

class SyncStatus(Base):
    __tablename__ = "sync_status"

    id = Column(Integer, primary_key=True)
    last_import_time = Column(DateTime)
class ImportLog(Base):
    __tablename__ = "import_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    matches_imported = Column(Integer, default=0)
    status = Column(String(255), default="OK")  # "OK" | "NO_NEW_MATCHES" | "ERROR"

    def __repr__(self):
        return f"<ImportLog {self.timestamp} ({self.status})>"
