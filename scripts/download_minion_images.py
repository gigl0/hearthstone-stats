import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path
import time

# Percorsi
MINIONS_JSON = "minions_bg.json"
IMAGES_DIR = Path("frontend/static/images/minions")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Carica minions
with open(MINIONS_JSON, encoding="utf-8") as f:
    minions = json.load(f)

for m_id, m_info in minions.items():
    name = m_info["name"]
    wiki_name = quote(name.replace(" ", "_"))
    url = f"https://hearthstone.fandom.com/wiki/{wiki_name}"
    print(f"Scaricando {name} da {url}...")

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Cerca prima immagine della carta
        img_tag = soup.select_one(".pi-image-collection img") or soup.select_one(".wikia-cardtable-card-image img")
        if img_tag:
            img_url = img_tag["src"]
            # Scarica l'immagine
            img_ext = img_url.split(".")[-1].split("?")[0]
            local_path = IMAGES_DIR / f"{m_id}.{img_ext}"
            
            # Scarica solo se non esiste già
            if not local_path.exists():
                img_data = requests.get(img_url).content
                local_path.write_bytes(img_data)
            
            # Aggiorna il dizionario
            m_info["image"] = f"frontend/static/images/minions/{m_id}.{img_ext}"
        else:
            print(f"Immagine non trovata per {name}, metto placeholder.")
            m_info["image"] = "frontend/static/images/minions/missing.png"

        # Piccola pausa per non stressare la wiki
        time.sleep(0.3)

    except Exception as e:
        print(f"Errore {name}: {e}")
        m_info["image"] = "frontend/static/images/minions/missing.png"

# Salva aggiornamenti
with open(MINIONS_JSON, "w", encoding="utf-8") as f:
    json.dump(minions, f, indent=4, ensure_ascii=False)

print("✅ Tutte le immagini aggiornate e salvate.")
