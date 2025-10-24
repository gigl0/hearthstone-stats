import json
from pathlib import Path

# === Percorsi ===
FRONTEND_JSON = Path("frontend-react/public/minions_bg.json")
MINION_DIR = Path("frontend-react/public/images/minions")

if not FRONTEND_JSON.exists():
    raise FileNotFoundError(f"❌ JSON non trovato: {FRONTEND_JSON}")

# === Carica JSON ===
with open(FRONTEND_JSON, encoding="utf-8") as f:
    data = json.load(f)

print(f"📦 {len(data)} minion caricati dal JSON\n")

fixed = 0
missing = []

for card_id, info in data.items():
    img_path = MINION_DIR / f"{card_id}.png"

    # Se l'immagine esiste e il campo image è vuoto o sbagliato
    if img_path.exists() and (not info.get("image") or "static" in info["image"]):
        info["image"] = f"/images/minions/{card_id}.png"
        fixed += 1
    elif not img_path.exists():
        missing.append(card_id)

# === Salva JSON aggiornato ===
with open(FRONTEND_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ {fixed} percorsi corretti in {FRONTEND_JSON}")
if missing:
    print(f"⚠️ Mancano {len(missing)} file immagine:")
    for m in missing[:20]:
        print(f"   - {m}")
    if len(missing) > 20:
        print("   ...")
