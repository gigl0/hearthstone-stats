import json
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
from sqlalchemy import update
from pathlib import Path

# === Percorsi ===
BACKEND_JSON = Path("app/data/heroes_bg.json")
FRONTEND_JSON = Path("frontend-react/public/heroes_bg.json")

# === Carica JSON Backend ===
with open(BACKEND_JSON, encoding="utf-8") as f:
    heroes_backend = json.load(f)

# === Carica JSON Frontend (se esiste) ===
if FRONTEND_JSON.exists():
    with open(FRONTEND_JSON, encoding="utf-8") as f:
        heroes_frontend = json.load(f)
else:
    heroes_frontend = {}

# === Crea mappe di lookup ===
id_to_name = {k: v["name"] for k, v in heroes_backend.items()}
name_to_id = {v["name"].lower(): k for k, v in heroes_backend.items()}

# === Connessione DB ===
db = SessionLocal()
rows = db.query(BattlegroundsMatch.hero_name).distinct().all()
names_in_db = [r[0] for r in rows if r[0]]

print(f"🧩 Eroi unici trovati nel DB: {len(names_in_db)}\n")

changes = []

for hero_name in names_in_db:
    hn = hero_name.strip()
    if hn in id_to_name.values():
        continue

    # 1️⃣ match diretto per ID
    if hn in id_to_name:
        correct_name = id_to_name[hn]
        changes.append((hn, correct_name))
        continue

    # 2️⃣ match parziale (case-insensitive)
    for hero_id, data in heroes_backend.items():
        if hn.lower() in hero_id.lower() or hero_id.lower() in hn.lower():
            correct_name = data["name"]
            changes.append((hn, correct_name))
            break

# === Mostra risultati ===
if not changes:
    print("✅ Tutti i nomi degli eroi nel DB sono già corretti.")
else:
    print("🔍 Correzioni trovate:")
    for old, new in changes:
        print(f"  - {old} → {new}")

    print(f"\nTotale correzioni trovate: {len(changes)}")

    # === Conferma ===
    choice = input("\nApplico modifiche al DB e JSON? (s/n): ").lower().strip()
    if choice == "s":
        # 1️⃣ Aggiorna DB
        for old, new in changes:
            db.execute(
                update(BattlegroundsMatch)
                .where(BattlegroundsMatch.hero_name == old)
                .values(hero_name=new)
            )
        db.commit()

        # 2️⃣ Aggiorna JSON frontend e backend se necessario
        for hero_id, data in heroes_backend.items():
            # Fix percorso immagini vecchi
            img_path = data.get("image", "")
            if "static\\" in img_path or "static/" in img_path:
                data["image"] = "/images/heroes/" + Path(img_path).name

        heroes_frontend.update(heroes_backend)

        # Salva entrambi i JSON aggiornati
        with open(BACKEND_JSON, "w", encoding="utf-8") as f:
            json.dump(heroes_backend, f, indent=4, ensure_ascii=False)

        with open(FRONTEND_JSON, "w", encoding="utf-8") as f:
            json.dump(heroes_frontend, f, indent=4, ensure_ascii=False)

        print("\n✅ Database e JSON frontend/public aggiornati con successo.")
    else:
        print("❌ Nessuna modifica applicata.")

db.close()
