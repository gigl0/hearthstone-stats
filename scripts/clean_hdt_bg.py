import csv
import json
from pathlib import Path
import io
from datetime import datetime

# === Percorsi file ===
ROOT = Path(__file__).parent.parent
CSV_FILE = ROOT / "parsed_games.csv"
HEROES_FILE = ROOT / "heroes_bg.json"
MINIONS_FILE = ROOT / "minions_bg.json"
OUTPUT_CSV = ROOT / "parsed_games_clean.csv"

# === 1️⃣ Carica mappa eroi ===
with io.open(HEROES_FILE, mode="r", encoding="utf-8", errors="ignore") as f:
    heroes_data = json.load(f)

hero_map = {}
for hero_id, hero in heroes_data.items():
    if "HERO" in hero_id:  # Solo eroi Battlegrounds
        hero_map[hero_id] = {
            "name": hero.get("name", hero_id),
            "image": hero.get("image", ""),
        }

print(f"✅ Loaded {len(hero_map)} heroes for mapping.")

# === 2️⃣ Carica mappa minion ===
with io.open(MINIONS_FILE, mode="r", encoding="utf-8", errors="ignore") as f:
    minions_data = json.load(f)

minion_map = {}
for minion_id, data in minions_data.items():
    minion_map[minion_id] = {
        "name": data.get("name", minion_id),
        "type": data.get("type", ""),
        "image": data.get("image", ""),
    }

print(f"✅ Loaded {len(minion_map)} minions for mapping.")

# === 3️⃣ Leggi CSV originale ===
with open(CSV_FILE, newline='', encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# === 4️⃣ Pulizia e arricchimento righe ===
for row in rows:
    # --- HERO DATA ---
    hero_id = row.get("hero", "")
    hero_info = hero_map.get(hero_id, {"name": hero_id, "image": ""})
    row["hero_name"] = hero_info["name"]
    row["hero_image"] = hero_info["image"]

    # --- DATE & DURATA ---
    try:
        start = datetime.fromisoformat(row["start_time"])
        end = datetime.fromisoformat(row["end_time"])
        duration = (end - start).total_seconds() / 60  # minuti
    except Exception:
        duration = ""
    row["duration_min"] = round(duration, 1) if duration else ""

    # --- RATING DELTA ---
    try:
        rating = int(row.get("rating", 0))
        rating_after = int(row.get("rating_after", 0))
        row["rating_delta"] = rating_after - rating
    except ValueError:
        row["rating_delta"] = ""

    # --- MINIONS ---
    minions_raw = row.get("minions", "")
    if minions_raw:
        minion_ids = [m.strip() for m in minions_raw.split("|") if m.strip()]
        minion_names = []
        minion_types = []
        minion_images = []

        for mid in minion_ids:
            m_info = minion_map.get(mid, {"name": mid, "type": "", "image": ""})
            minion_names.append(m_info["name"])
            minion_types.append(m_info["type"])
            minion_images.append(m_info["image"])

        row["minions_count"] = len(minion_names)
        row["minions_list"] = ", ".join(minion_names)
        row["minion_types"] = ", ".join(sorted(set(minion_types)))  # es: "BEAST, QUILBOAR"
        row["minion_images"] = "|".join(minion_images)  # utile per frontend
    else:
        row["minions_count"] = 0
        row["minions_list"] = ""
        row["minion_types"] = ""
        row["minion_images"] = ""

    # --- GAME RESULT ---
    try:
        placement = int(row.get("placement", 0))
        if placement == 1:
            result = "win"
        elif 2 <= placement <= 4:
            result = "top4"
        elif 5 <= placement <= 8:
            result = "loss"
        else:
            result = "unknown"
    except ValueError:
        result = "unknown"
    row["game_result"] = result

# === 5️⃣ Scrittura CSV finale ===
base_fields = [
    "player_id", "hero", "hero_name", "hero_image",
    "start_time", "end_time", "duration_min",
    "placement", "game_result",
    "rating", "rating_after", "rating_delta",
    "minions", "minions_count", "minions_list",
    "minion_types", "minion_images"
]

extra_fields = [f for f in rows[0].keys() if f not in base_fields]
output_fields = base_fields + extra_fields

with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"💾 Cleaned CSV saved to {OUTPUT_CSV}")
print(f"📊 Columns: {', '.join(output_fields)}")
