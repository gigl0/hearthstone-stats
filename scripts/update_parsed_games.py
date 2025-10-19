import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "hearthstone_bg.db")
conn = sqlite3.connect("hearthstone_bg.db")


def init_db():
    """Crea la tabella se non esiste già"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battlegrounds_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT,
            hero TEXT,
            start_time TEXT,
            end_time TEXT,
            placement INTEGER,
            rating INTEGER,
            rating_after INTEGER,
            minions TEXT
        )
    """)
    conn.commit()
    conn.close()

def update_from_hdt_logs(xml_file_path):
    """Legge un XML di HDT e aggiorna il DB"""
    xml_file_path = Path(xml_file_path)
    if not xml_file_path.exists():
        print(f"[!] File not found: {xml_file_path}")
        return

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for game in root.findall("Game"):
        player_id = game.get("Player")
        hero = game.get("Hero")
        start_time = game.get("StartTime")
        end_time = game.get("EndTime")
        placement = int(game.get("Placemenent") or game.get("Placement") or 0)
        rating = int(game.get("Rating") or 0)
        rating_after = int(game.get("RatingAfter") or 0)

        # Lista dei minions
        minions = []
        final_board = game.find("FinalBoard")
        if final_board:
            for m in final_board.findall("Minion"):
                card_id = m.findtext("CardId")
                if card_id:
                    minions.append(card_id)
        minions_str = ";".join(minions)

        # Evita duplicati
        cursor.execute("""
            SELECT id FROM battlegrounds_matches
            WHERE player_id=? AND start_time=?
        """, (player_id, start_time))
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO battlegrounds_matches 
            (player_id, hero, start_time, end_time, placement, rating, rating_after, minions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (player_id, hero, start_time, end_time, placement, rating, rating_after, minions_str))

    conn.commit()
    conn.close()
    print(f"[✓] Updated DB from {xml_file_path.name}")


if __name__ == "__main__":
    init_db()
    logs_dir = Path.home() / "Documents/Hearthstone/Decks/BattlegroundsLogs"
    for xml_file in logs_dir.glob("BgsLastGames*.xml"):
        update_from_hdt_logs(xml_file)
