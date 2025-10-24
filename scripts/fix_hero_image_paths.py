import json
from pathlib import Path

# === Percorsi ===
FRONTEND_JSON = Path("frontend-react/public/heroes_bg.json")
HEROES_DIR = Path("frontend-react/public/images/heroes")

# === Carica JSON ===
if not FRONTEND_JSON.exists():
    raise FileNotFoundError(f"❌ File non trovato: {FRONTEND_JSON}")

with open(FRONTEND_JSON, encoding="utf-8") as f:
    heroes = json.load(f)

print(f"📦 {len(heroes)} eroi caricati dal JSON\n")

updated = 0
missing = []

for hero_id, data in heroes.items():
    img_name = f"{hero_id}.png"
    local_path = HEROES_DIR / img_name

    if local_path.exists():
        # Aggiorna percorso immagine nel JSON
        data["image"] = f"/images/heroes/{img_name}"
        updated += 1
    else:
        missing.append(hero_id)

# === Salvataggio ===
with open(FRONTEND_JSON, "w", encoding="utf-8") as f:
    json.dump(heroes, f, indent=4, ensure_ascii=False)

print(f"✅ {updated} percorsi aggiornati nel JSON")
if missing:
    print(f"⚠️ Mancano {len(missing)} immagini locali:")
    for m in missing[:20]:
        print(f"   - {m}")
    if len(missing) > 20:
        print("   ...")
