import json
from pathlib import Path

# === Percorsi principali ===
BACKEND_JSON = Path("app/data/minions_bg.json")
FRONTEND_JSON = Path("frontend-react/public/minions_bg.json")
MINION_DIR = Path("frontend-react/public/images/minions")

def fix_json(json_path: Path):
    if not json_path.exists():
        print(f"❌ JSON non trovato: {json_path}")
        return 0, 0

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    fixed = 0
    missing = []

    for card_id, info in data.items():
        img_path = MINION_DIR / f"{card_id}.png"

        # Corregge solo se il file esiste
        if img_path.exists():
            correct_path = f"/images/minions/{card_id}.png"
            if info.get("image") != correct_path:
                info["image"] = correct_path
                fixed += 1
        else:
            missing.append(card_id)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return fixed, len(missing)


def main():
    print("🔧 Correzione percorsi immagini minion...\n")

    total_fixed, total_missing = 0, 0

    for label, json_path in {
        "Backend": BACKEND_JSON,
        "Frontend": FRONTEND_JSON
    }.items():
        fixed, missing = fix_json(json_path)
        total_fixed += fixed
        total_missing += missing

        print(f"✅ {fixed} percorsi corretti in {json_path}")
        if missing:
            print(f"⚠️ Mancano {missing} immagini locali per {label}\n")

    print("\n🏁 Operazione completata!")
    print(f"📊 Totale percorsi corretti: {total_fixed}")
    print(f"🧩 Immagini mancanti totali: {total_missing}")


if __name__ == "__main__":
    main()
