import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from pathlib import Path

# Carica le variabili dal file .env (per PostgreSQL)
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Percorso del DB SQLite locale
SQLITE_DB = Path(__file__).parent.parent / "hearthstone_bg.db"

def migrate_sqlite_to_postgres():
    if not SQLITE_DB.exists():
        print(f"❌ File SQLite non trovato: {SQLITE_DB}")
        return

    # Connessione a SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM battlegrounds_matches")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print("⚠️ Nessun record trovato in SQLite.")
        return

    # Connessione a PostgreSQL
    pg_conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    pg_cursor = pg_conn.cursor()

    # Crea tabella se non esiste
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS battlegrounds_matches (
            id SERIAL PRIMARY KEY,
            player_id TEXT,
            hero TEXT,
            start_time TEXT,
            end_time TEXT,
            placement INTEGER,
            rating INTEGER,
            rating_after INTEGER,
            minions TEXT
        );
    """)

    # Inserisci dati
    print(f"➡️ Importing {len(rows)} records from SQLite...")
    execute_values(
        pg_cursor,
        """
        INSERT INTO battlegrounds_matches
        (id, player_id, hero, start_time, end_time, placement, rating, rating_after, minions)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        rows
    )

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("✅ Migration completed successfully!")


if __name__ == "__main__":
    migrate_sqlite_to_postgres()
