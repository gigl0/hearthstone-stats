import os
import csv
import xml.etree.ElementTree as ET

# === Percorso file sorgente HDT ===
HDT_LOG_PATH = os.path.expanduser("~/AppData/Roaming/HearthstoneDeckTracker/BgsLastGames.xml")

# === Percorso di output nel progetto ===
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "parsed_games.csv")

def parse_hdt_xml(xml_path):
    games = []
    if not os.path.exists(xml_path):
        print(f"❌ File non trovato: {xml_path}")
        return games

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for game in root.findall("Game"):
        player_id = game.get("Player", "")
        hero = game.get("Hero", "")
        start_time = game.get("StartTime", "")
        end_time = game.get("EndTime", "")
        placement = game.get("Placemenent", "")  # attenzione: è scritto così nel file!
        rating = game.get("Rating", "")
        rating_after = game.get("RatingAfter", "")

        # Minions
        minions = []
        final_board = game.find("FinalBoard")
        if final_board is not None:
            for minion in final_board.findall("Minion"):
                card = minion.find("CardId")
                if card is not None and card.text:
                    minions.append(card.text)
        minions_str = ";".join(minions)

        games.append([
            player_id,
            hero,
            start_time,
            end_time,
            placement,
            rating,
            rating_after,
            minions_str
        ])

    return games


def update_csv():
    games = parse_hdt_xml(HDT_LOG_PATH)
    if not games:
        return

    header = ["player_id", "hero", "start_time", "end_time", "placement", "rating", "rating_after", "minions"]

    # Leggiamo l’esistente per evitare duplicati
    existing = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                key = (row[2], row[3], row[1])  # start_time + end_time + hero
                existing.add(key)

    # Append solo partite nuove
    new_rows = [g for g in games if (g[2], g[3], g[1]) not in existing]

    if new_rows:
        write_mode = "a" if os.path.exists(OUTPUT_CSV) else "w"
        with open(OUTPUT_CSV, write_mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_mode == "w":
                writer.writerow(header)
            writer.writerows(new_rows)
        print(f"✅ {len(new_rows)} nuove partite aggiunte a parsed_games.csv")
    else:
        print("⚙️ Nessuna nuova partita trovata.")


if __name__ == "__main__":
    update_csv()
import os
import csv
import xml.etree.ElementTree as ET

# === Percorso file sorgente HDT ===
HDT_LOG_PATH = os.path.expanduser("~/AppData/Roaming/HearthstoneDeckTracker/BgsLastGames.xml")

# === Percorso di output nel progetto ===
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "parsed_games.csv")

def parse_hdt_xml(xml_path):
    games = []
    if not os.path.exists(xml_path):
        print(f"❌ File non trovato: {xml_path}")
        return games

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for game in root.findall("Game"):
        player_id = game.get("Player", "")
        hero = game.get("Hero", "")
        start_time = game.get("StartTime", "")
        end_time = game.get("EndTime", "")
        placement = game.get("Placemenent", "")  # attenzione: è scritto così nel file!
        rating = game.get("Rating", "")
        rating_after = game.get("RatingAfter", "")

        # Minions
        minions = []
        final_board = game.find("FinalBoard")
        if final_board is not None:
            for minion in final_board.findall("Minion"):
                card = minion.find("CardId")
                if card is not None and card.text:
                    minions.append(card.text)
        minions_str = ";".join(minions)

        games.append([
            player_id,
            hero,
            start_time,
            end_time,
            placement,
            rating,
            rating_after,
            minions_str
        ])

    return games


def update_csv():
    games = parse_hdt_xml(HDT_LOG_PATH)
    if not games:
        return

    header = ["player_id", "hero", "start_time", "end_time", "placement", "rating", "rating_after", "minions"]

    # Leggiamo l’esistente per evitare duplicati
    existing = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                key = (row[2], row[3], row[1])  # start_time + end_time + hero
                existing.add(key)

    # Append solo partite nuove
    new_rows = [g for g in games if (g[2], g[3], g[1]) not in existing]

    if new_rows:
        write_mode = "a" if os.path.exists(OUTPUT_CSV) else "w"
        with open(OUTPUT_CSV, write_mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_mode == "w":
                writer.writerow(header)
            writer.writerows(new_rows)
        print(f"✅ {len(new_rows)} nuove partite aggiunte a parsed_games.csv")
    else:
        print("⚙️ Nessuna nuova partita trovata.")


if __name__ == "__main__":
    update_csv()
    print("✅ Aggiornamento CSV completato.") 