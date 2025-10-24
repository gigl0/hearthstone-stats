import json
import requests
from pathlib import Path
import time

# === Percorsi ===
HEROES_JSON = Path("app/data/heroes_bg.json")
IMAGES_DIR = Path("frontend-react/public/images/heroes")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
MISSING_FILE = Path("missing_heroes.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# === Funzione robusta per leggere JSON ===
def safe_json_load(path: Path):
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"❌ Impossibile leggere {path}")

# === Carica gli eroi ===
heroes = safe_json_load(HEROES_JSON)
missing = []

print("🚀 Download immagini Battlegrounds HEROES (HSReplay + HearthstoneJSON)\n")

for h_id, h_info in heroes.items():
    name = h_info.get("name", "").strip()
    if not name:
        continue

    print(f"🔍 [{h_id}] {name}")

    # URL diretto al CDN HearthstoneJSON (prioritario)
    img_url = f"https://art.hearthstonejson.com/v1/heroes/latest/256x/{h_id}.png"

    try:
        r = requests.get(img_url, headers=HEADERS, timeout=8)
        if r.status_code == 200 and len(r.content) > 1000:
            # Salva l'immagine
            local_path = IMAGES_DIR / f"{h_id}.png"
            if not local_path.exists():
                local_path.write_bytes(r.content)

            h_info["image"] = f"/images/heroes/{h_id}.png"
            print(f"✅ Scaricato da HearthstoneJSON")
        else:
            print(f"⚠️ Non trovato su CDN ({r.status_code})")
            missing.append(name)
            h_info["image"] = "/images/heroes/placeholder.png"

    except Exception as e:
        print(f"❌ Errore {name}: {e}")
        h_info["image"] = "/images/heroes/placeholder.png"
        missing.append(name)

    time.sleep(0.15)  # rate limit gentile

# === Salva risultati aggiornati ===
with open(HEROES_JSON, "w", encoding="utf-8") as f:
    json.dump(heroes, f, indent=4, ensure_ascii=False)

with open(MISSING_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(missing))

print(f"\n✅ Download completato. Immagini salvate in {IMAGES_DIR}")
print(f"🧮 Eroi mancanti: {len(missing)} (vedi {MISSING_FILE})")
