import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path
import time
import json
import argparse

# === CONFIG ===
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
DELAY = 0.25

# CDN ufficiali HearthstoneJSON
CDN_MINION = "https://art.hearthstonejson.com/v1/render/latest/enUS/512x/"
CDN_HERO = "https://art.hearthstonejson.com/v1/heroes/latest/256x/"
BASE_WIKI = "https://hearthstone.fandom.com/wiki/"

# === FILE DI INPUT ===
TARGETS = {
    "minions": (
        "app/data/minions_bg.json",
        "frontend-react/public/images/minions",
        "missing_images.txt",
    ),
    "heroes": (
        "app/data/heroes_bg.json",
        "frontend-react/public/images/heroes",
        "missing_heroes.txt",
    ),
}

# cache globale per HearthstoneJSON
_blizzard_data = {"minions": None, "heroes": None}


# ============================================================
# API HearthstoneJSON (fonte principale)
# ============================================================
def fetch_from_blizzard_api(name: str, is_hero: bool) -> str | None:
    """
    Tenta di trovare l’immagine usando HearthstoneJSON CDN (dati ufficiali).
    """
    global _blizzard_data
    key = "heroes" if is_hero else "minions"

    if _blizzard_data[key] is None:
        try:
            url = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
            print(f"🌍 Download lista carte da {url} ...")
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            cards = r.json()

            # Filtra solo Battlegrounds
            bg_cards = [
                c for c in cards
                if c.get("techLevel") or c.get("battlegroundsHero")
            ]

            mapping = {c["name"].lower(): c["id"] for c in bg_cards if "name" in c and "id" in c}
            _blizzard_data[key] = mapping
            print(f"📦 Cache {key} caricata con {len(mapping)} carte BG.")
        except Exception as e:
            print(f"⚠️ Errore fetch HearthstoneJSON {key}: {e}")
            _blizzard_data[key] = {}

    data = _blizzard_data[key]

    # match flessibile (anche per "Golden" o simili)
    card_id = next((v for k, v in data.items() if name.lower() in k), None)
    if card_id:
        cdn = CDN_HERO if is_hero else CDN_MINION
        return f"{cdn}{card_id}.png"
    return None


# ============================================================
# Wiki Hearthstone Fandom (fallback)
# ============================================================
def fetch_from_fandom(name: str) -> str | None:
    """Fallback su Hearthstone Wiki (EN)."""
    wiki_name = quote(name.replace(" ", "_"))
    url = BASE_WIKI + wiki_name
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")

        img_tag = (
            soup.select_one(".pi-image-collection img")
            or soup.select_one(".wikia-cardtable-card-image img")
            or soup.select_one(".pi-image img")
            or soup.select_one(".wikia-gallery-item img")
            or soup.select_one(".wikia-gallery img")
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


# ============================================================
# Ricerca immagine completa
# ============================================================
def fetch_image_url(name: str, card_id: str, is_hero: bool) -> str | None:
    """
    Ricerca completa dell'immagine:
    1️⃣ HearthstoneJSON ufficiale
    2️⃣ CDN Blizzard CloudFront con ID e slug multipli
    3️⃣ Wiki Fandom fallback
    """
    # 1️⃣ HearthstoneJSON CDN
    url = fetch_from_blizzard_api(name, is_hero)
    if url:
        return url

    # 2️⃣ Blizzard CloudFront (tenta ID multipli e nomi normalizzati)
    try:
        slug = (
            name.lower()
            .replace("'", "")
            .replace(",", "")
            .replace("’", "")
            .replace(":", "")
            .replace(".", "")
            .replace(" ", "-")
        )

        # pattern di ID alternativi (alcuni eroi hanno skin/varianti)
        candidate_ids = [
            card_id,
            f"{card_id}_SKIN_001",
            f"{card_id}_SKIN_002",
            f"{card_id}_ALT_001",
            f"{card_id}_ALT_002",
            f"{card_id}_GOLDEN",
            f"{card_id}_FULL",
            f"BG_HERO_{card_id}",
        ]

        # URL possibili su CloudFront e CDN
        test_urls = []
        cdn_prefixes = [
            "https://d15f34w2p8l1cc.cloudfront.net/hearthstone/",
            "https://art.hearthstonejson.com/v1/heroes/latest/enUS/256x/",
            "https://art.hearthstonejson.com/v1/render/latest/enUS/512x/",
        ]

        # costruisci tutte le varianti possibili
        for prefix in cdn_prefixes:
            for cid in candidate_ids:
                test_urls.append(f"{prefix}{cid}.png")
            # anche versioni basate sul nome “slug”
            test_urls.append(f"{prefix}{slug}.png")
            test_urls.append(f"{prefix}{slug.replace('-', '_')}.png")

        for turl in test_urls:
            try:
                r = requests.head(turl, headers=HEADERS, timeout=4)
                if r.status_code == 200:
                    print(f"🧩 Fallback CloudFront trovato per {name}")
                    return turl
            except Exception:
                continue
    except Exception:
        pass

    # 3️⃣ Wiki Fandom (fallback finale)
    wiki_url = fetch_from_fandom(name)
    if wiki_url:
        print(f"🌐 Wiki fallback per {name}")
        return wiki_url

    return None




# ============================================================
# Processamento file JSON
# ============================================================
def process_file(json_path: str, images_dir: str, missing_txt: str, label: str):
    json_file = Path(json_path)
    images_path = Path(images_dir)
    missing_file = Path(missing_txt)

    if not json_file.exists() or not missing_file.exists():
        print(f"❌ File mancante: {json_file} o {missing_file}")
        return

    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(json_file, encoding=enc) as f:
                data = json.load(f)
            break
        except UnicodeDecodeError:
            continue

    missing_names = [
        n.strip() for n in missing_file.read_text(encoding="utf-8").splitlines() if n.strip()
    ]
    fixed = []
    is_hero = label == "heroes"

    print(f"\n⚙️  Inizio recupero per {label} ({len(missing_names)} mancanti)...")

    for name in missing_names:
        print(f"🔄 Tentativo di recupero: {name}")
        entry = next(((k, v) for k, v in data.items() if v.get("name") == name), None)
        if not entry:
            print(f"⚠️  Nessun ID trovato per {name}")
            continue

        card_id, info = entry
        img_url = fetch_image_url(name, card_id, is_hero)

        if img_url:
            try:
                ext = img_url.split(".")[-1].split("?")[0]
                if len(ext) > 4:
                    ext = "png"
                dest_file = images_path / f"{card_id}.{ext}"
                if not dest_file.exists():
                    img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                    dest_file.write_bytes(img_data)
                info["image"] = f"/images/{images_path.name}/{card_id}.{ext}"
                fixed.append(name)
                print(f"✅ Recuperato: {name}")
            except Exception as e:
                print(f"⚠️ Errore salvataggio {name}: {e}")
        else:
            print(f"🚫 Ancora nessuna immagine trovata per {name}")
        time.sleep(DELAY)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    still_missing = [n for n in missing_names if n not in fixed]
    missing_file.write_text("\n".join(still_missing), encoding="utf-8")

    print(f"\n📊 {len(fixed)} immagini recuperate, {len(still_missing)} ancora mancanti.")
    print(f"📁 Aggiornato: {json_file}")
    print(f"📄 Lista rimanenti: {missing_file}")


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Recupera immagini mancanti da HearthstoneJSON (EN).")
    parser.add_argument("--only", choices=["minions", "heroes"], help="Esegui solo su una categoria")
    args = parser.parse_args()

    for label, (json_path, images_dir, missing_txt) in TARGETS.items():
        if args.only and args.only != label:
            continue
        process_file(json_path, images_dir, missing_txt, label)

    print("\n🏁 Re-analisi completata!")


if __name__ == "__main__":
    main()
