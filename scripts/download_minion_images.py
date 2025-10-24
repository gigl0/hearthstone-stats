import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path
import time

# === Percorsi ===
MINIONS_JSON = Path("app/data/minions_bg.json")
IMAGES_DIR = Path("frontend-react/public/images/minions")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
MISSING_FILE = Path("missing_images.txt")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# === Caricamento Minion ===
with open(MINIONS_JSON, encoding="utf-8") as f:
    minions = json.load(f)

missing = []

for m_id, m_info in minions.items():
    name = m_info.get("name", "").strip()
    if not name:
        continue

    wiki_name = quote(name.replace(" ", "_"))
    url = f"https://hearthstone.fandom.com/wiki/{wiki_name}"
    print(f"🔍 [{m_id}] {name} → {url}")

    img_url = None

    try:
        # ======== 1️⃣ Wiki Hearthstone Fandom ========
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 404:
            raise ValueError("Page not found")
        soup = BeautifulSoup(r.text, "html.parser")

        # === 1° tentativo: immagine principale (box carta) ===
        img_tag = (
            soup.select_one(".pi-image-collection img")
            or soup.select_one(".wikia-cardtable-card-image img")
            or soup.select_one(".pi-image img")
        )

        # === 2° tentativo: immagine full art o gallery ===
        if not img_tag:
            img_tag = (
                soup.select_one(".wikia-gallery-item img")
                or soup.select_one(".wikia-gallery img")
                or soup.select_one(".thumbimage")
            )

        # === se trovata, normalizza URL ===
        if img_tag and img_tag.get("src"):
            img_url = img_tag["src"]
            # 🔧 pulizia URL per togliere /revision/latest/...
            if "/revision/" in img_url:
                img_url = img_url.split("/revision/")[0]
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            print(f"🎨 Immagine trovata su wiki → {img_url.split('/')[-1]}")
        else:
            raise ValueError("No image found on wiki")

    except Exception as e:
        print(f"⚠️ Wiki fallita per {name}: {e}")
        # ======== 2️⃣ Fallback: HearthstoneJSON CDN ========
        try:
            fallback_url = f"https://art.hearthstonejson.com/v1/render/latest/enUS/512x/{m_id}.png"
            test = requests.get(fallback_url, headers=HEADERS, timeout=5)
            if test.status_code == 200:
                img_url = fallback_url
                print(f"🧩 Fallback trovato per {m_id}")
            else:
                raise ValueError("Fallback not available")
        except Exception:
            img_url = None

    # === Download immagine ===
    if img_url:
        try:
            ext = img_url.split(".")[-1].split("?")[0]
            if len(ext) > 4:
                ext = "png"  # fix per URL strani
            local_path = IMAGES_DIR / f"{m_id}.{ext}"

            if not local_path.exists():
                img_data = requests.get(img_url, headers=HEADERS).content
                local_path.write_bytes(img_data)

            m_info["image"] = f"/images/minions/{m_id}.{ext}"
        except Exception as e:
            print(f"❌ Errore salvataggio {name}: {e}")
            m_info["image"] = "/images/minions/placeholder.png"
            missing.append(name)
    else:
        print(f"🚫 Nessuna immagine trovata per {name}")
        m_info["image"] = "/images/minions/placeholder.png"
        missing.append(name)

    time.sleep(0.25)  # evita rate limit

# === Salva risultati aggiornati ===
with open(MINIONS_JSON, "w", encoding="utf-8") as f:
    json.dump(minions, f, indent=4, ensure_ascii=False)

with open(MISSING_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(missing))

print(f"\n✅ Download completato. Immagini salvate in {IMAGES_DIR}")
print(f"🧮 Minion mancanti: {len(missing)} (vedi {MISSING_FILE})")
