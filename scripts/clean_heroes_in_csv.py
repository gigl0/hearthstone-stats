import csv
import json
from pathlib import Path
import io
# Percorsi file
ROOT = Path(__file__).parent.parent
CSV_FILE = ROOT / "parsed_games.csv"
HEROES_FILE = ROOT / "heroes_bg.json"
OUTPUT_CSV = ROOT / "parsed_games_clean.csv"

# Carica mappa eroi

with io.open(HEROES_FILE, mode="r", encoding="utf-8", errors="ignore") as f:
    heroes_data = json.load(f)


# Crea dizionario con ID → Nome
hero_map = {}
for hero_id, hero in heroes_data.items():
    # Filtra solo gli eroi Battlegrounds (quelli che iniziano con BG o TB_BaconShop)
    if "HERO" in hero_id:
        hero_map[hero_id] = {
            "name": hero.get("name", hero_id),
            "image": hero.get("image", ""),
        }

print(f"✅ Loaded {len(hero_map)} heroes for mapping.")

# Leggi CSV originale
with open(CSV_FILE, newline='', encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Pulizia e sostituzione nomi eroi
for row in rows:
    hero_id = row["hero"]
    hero_info = hero_map.get(hero_id)
    if hero_info:
        row["hero_name"] = hero_info["name"]
        row["hero_image"] = hero_info["image"]
    else:
        row["hero_name"] = hero_id
        row["hero_image"] = ""

# Scrivi nuovo CSV
output_fields = list(rows[0].keys())
if "hero_name" not in output_fields:
    output_fields += ["hero_name", "hero_image"]

with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"💾 Cleaned CSV saved to {OUTPUT_CSV}")
