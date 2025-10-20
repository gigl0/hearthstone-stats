import csv
import json
from pathlib import Path
import io
from datetime import datetime

# === Percorsi file ===
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "app" / "data"

CSV_FILE = DATA_DIR / "parsed_games_clean.csv"   # file di input
HEROES_FILE = DATA_DIR / "heroes_bg.json"
MINIONS_FILE = DATA_DIR / "minions_bg.json"
OUTPUT_CSV = DATA_DIR / "parsed_games_clean.csv" # output sovrascritto

# === 1️⃣ Carica mappa eroi ===
with io.open(HEROES_FILE, mode="r", encoding="utf-8", errors="ignore") as f:
    heroes_data = json.load(f)

hero_map = {}
for hero_id, hero in heroes_data.items():
    if "HERO" in hero_id:  # Solo Battlegrounds
        hero_map[hero_id] = {
            "name": hero.get("name", hero_id),
            "image": hero.get("image", "")
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
        "image": data.get("image", "")
    }

print(f"✅ Loaded {len(minion_map)} minions for mapping.")

# === 3️⃣ Leggi CSV originale ===
with open(CSV_FILE, newline='', encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# === 4️⃣ Pulizia e arricchimento ===
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
        duration = (end - start).total_seconds() / 60
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
        # Supporta sia ";" che "|", e rimuove spazi
        minion_ids = [m.strip() for m in minions_raw.replace("|", ";").split(";") if m.strip()]
        minion_names, minion_types, minion_images = [], [], []

        for mid in minion_ids:
            # Rimuove suffisso dorato (_G) e normalizza maiuscole
            base_id = mid.replace("_G", "").strip().upper()

            # Cerca nel dizionario minion_map
            m_info = minion_map.get(base_id)
            if not m_info:
                # fallback: match parziale (alcuni minion cambiano ID versione)
                match = next((v for k, v in minion_map.items() if base_id in k or k in base_id), None)
                m_info = match or {"name": base_id, "type": "", "image": ""}

            minion_names.append(m_info["name"])
            minion_types.append(m_info["type"])
            minion_images.append(m_info["image"])

        row["minions_count"] = len(minion_names)
        row["minions_list"] = ", ".join(minion_names)
        row["minion_types"] = ", ".join(sorted(set(t for t in minion_types if t)))
        row["minion_images"] = "|".join(minion_images)
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