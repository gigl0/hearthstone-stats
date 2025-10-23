from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# ======================================================
# 🐘 CONFIGURAZIONE DATABASE - PostgreSQL
# ======================================================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Engine ---
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # verifica connessione attiva prima di usarla
    pool_size=10,         # connessioni persistenti
    max_overflow=20,      # connessioni temporanee extra
    future=True,
    echo=False            # metti True solo per debug SQL
)

# --- Session factory ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- DICHIARAZIONE BASE (!!! fondamentale !!!) ---
Base = declarative_base()

# --- get_db(): dipendenza per i router ---
def get_db():
    """Fornisce una sessione DB per ogni richiesta API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
