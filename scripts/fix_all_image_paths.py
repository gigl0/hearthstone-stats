import json
from pathlib import Path

# === Cartelle da correggere (backend + frontend) ===
BASE_DIRS = [
    Path("app/data"),
    Path("frontend-react/public"),
]

# === File attesi ===
FILES = ["minions_bg.json", "heroes_bg.json"]

def normalize_image_path(img: str) -> str:
    """Normalizza e corregge il percorso dell'immagine."""
    if not img:
        return ""

    img = img.replace("\\", "/").strip()

    # Se è un URL assoluto, lasciamolo intatto
    if img.startswith("http://") or img.startswith("https://"):
        return img

    # Rimuovi prefissi superflui
    if img.startswith("static/"):
        img = img[len("static/"):]
    if img.startswith("public/"):
        img = img[len("public/"):]

    # Assicura il prefisso /
    if not img.startswith("/"):
        img = "/" + img

    return img


for base_dir in BASE_DIRS:
    if not base_dir.exists():
        print(f"⚠️  Cartella mancante: {base_dir}")
        continue

    for filename in FILES:
        path = base_dir / filename
        if not path.exists():
            print(f"❌ File non trovato: {path}")
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            data = json.loads(path.read_text(encoding="latin-1"))

        modified = 0
        for v in data.values():
            if "image" in v:
                old = v["image"]
                new = normalize_image_path(old)
                if new != old:
                    v["image"] = new
                    modified += 1

        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        print(f"✅ {modified} percorsi corretti in {path.relative_to(Path('.'))}")
