import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path
import time

# === Percorsi ===
BACKEND_JSON = Path("app/data/minions_bg.json")
FRONTEND_JSON = Path("frontend-react/public/minions_bg.json")
IMAGES_DIR = Path("frontend-react/public/images/minions")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
MISSING_FILE = Path("missing_minions.txt")

# === Config ===
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
CDN_BASE = "https://art.hearthstonejson.com/v1/render/latest/enUS/512x/"
WIKI_BASE = "https://hearthstone.fandom.com/wiki/"
DELAY = 0.25  # anti-rate limit

def fetch_from_cdn(card_id: str) -> str | None:
    """Prova prima dalla CDN HearthstoneJSON."""
    url = f"{CDN_BASE}{card_id}.png"
    try:
        r = requests.head(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return url
    except Exception:
        pass
    return None


def fetch_from_wiki(name: str) -> str | None:
    """Prova dalla wiki Hearthstone EN."""
    wiki_name = quote(name.replace(" ", "_"))
    url = WIKI_BASE + wiki_name
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")

        img_tag = (
            soup.select_one(".pi-image-collection img")
            or soup.select_one(".wikia-cardtable-card-image img")
            or soup.select_one(".pi-image img")
            or soup.select_one(".thumbimage")
        )

        if not img_tag or not img_tag.get("src"):
            return None
        img_url = img_tag["src"]
        if "/revision/" in img_url:
            img_url = img_url.split("/revision/")[0]
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        return img_url
    except Exception:
        return None


def update_json(json_path: Path, updated_data: dict):
    """Salva in modo sicuro il file JSON aggiornato."""
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)


def process_minions(json_path: Path) -> list[str]:
    """Scarica e aggiorna le immagini mancanti per un file JSON."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    missing = []
    for card_id, info in data.items():
        name = info.get("name", "").strip()
        if not name:
            continue

        img_path = IMAGES_DIR / f"{card_id}.png"

        # già presente → skip
        if img_path.exists() and info.get("image"):
            continue

        print(f"🔄 {card_id}: {name}")
        img_url = fetch_from_cdn(card_id)

        if not img_url:
            img_url = fetch_from_wiki(name)

        if img_url:
            try:
                img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                img_path.write_bytes(img_data)
                info["image"] = f"/images/minions/{card_id}.png"
                print(f"✅ Salvata immagine {card_id}")
            except Exception as e:
                print(f"❌ Errore salvataggio {name}: {e}")
                info["image"] = "/images/minions/placeholder.png"
                missing.append(name)
        else:
            print(f"🚫 Nessuna immagine trovata per {name}")
            info["image"] = "/images/minions/placeholder.png"
            missing.append(name)

        time.sleep(DELAY)

    update_json(json_path, data)
    return missing


def main():
    print("⚙️  Avvio recupero immagini mancanti per i minion...\n")

    all_missing = []

    for label, path in [("Backend", BACKEND_JSON), ("Frontend", FRONTEND_JSON)]:
        print(f"📁 Lavorando su {label}: {path}")
        missing = process_minions(path)
        all_missing.extend(missing)
        print(f"✅ {label} aggiornato ({len(missing)} mancanti)\n")

    with open(MISSING_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(all_missing))))

    print(f"🏁 Completato! Immagini salvate in {IMAGES_DIR}")
    print(f"📄 Mancanti totali: {len(all_missing)} (vedi {MISSING_FILE})")


if __name__ == "__main__":
    main()
