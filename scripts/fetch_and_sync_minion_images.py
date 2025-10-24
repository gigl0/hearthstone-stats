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
DELAY = 0.25


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


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def sync_backend_frontend(backend: dict, frontend: dict):
    """Copia i campi image dove uno dei due li ha e l'altro no."""
    for k, v in backend.items():
        f_entry = frontend.get(k)
        if not f_entry:
            continue

        b_img, f_img = v.get("image", ""), f_entry.get("image", "")
        if not b_img and f_img:
            v["image"] = f_img
        elif not f_img and b_img:
            f_entry["image"] = b_img


def process_minions(data: dict, label: str) -> list[str]:
    missing = []
    for card_id, info in data.items():
        name = info.get("name", "").strip()
        if not name:
            continue

        local_path = IMAGES_DIR / f"{card_id}.png"

        # ✅ se file esiste localmente → aggiorna percorso
        if local_path.exists():
            correct = f"/images/minions/{card_id}.png"
            if info.get("image") != correct:
                info["image"] = correct
            continue

        # ❌ se campo image mancante → tenta recupero remoto
        if not info.get("image") or "placeholder" in info["image"]:
            print(f"🔄 [{label}] {card_id}: {name}")
            img_url = fetch_from_cdn(card_id) or fetch_from_wiki(name)

            if img_url:
                try:
                    img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                    local_path.write_bytes(img_data)
                    info["image"] = f"/images/minions/{card_id}.png"
                    print(f"✅ Salvata {card_id}")
                except Exception as e:
                    print(f"⚠️ Errore salvataggio {name}: {e}")
                    missing.append(name)
            else:
                print(f"🚫 Nessuna immagine trovata per {name}")
                missing.append(name)
            time.sleep(DELAY)
    return missing


def main():
    print("⚙️ Avvio sincronizzazione e recupero immagini mancanti...\n")

    backend = load_json(BACKEND_JSON)
    frontend = load_json(FRONTEND_JSON)

    # 1️⃣ Sincronizza tra backend e frontend
    sync_backend_frontend(backend, frontend)

    # 2️⃣ Completa dove manca
    missing_b = process_minions(backend, "Backend")
    missing_f = process_minions(frontend, "Frontend")

    # 3️⃣ Salva aggiornati
    save_json(BACKEND_JSON, backend)
    save_json(FRONTEND_JSON, frontend)

    all_missing = sorted(set(missing_b + missing_f))
    with open(MISSING_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(all_missing))

    print("\n🏁 Completato!")
    print(f"✅ Backend aggiornato ({len(backend)} minion)")
    print(f"✅ Frontend aggiornato ({len(frontend)} minion)")
    print(f"🧩 Mancanti totali: {len(all_missing)} (vedi {MISSING_FILE})")


if __name__ == "__main__":
    main()
