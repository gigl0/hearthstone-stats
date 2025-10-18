import os
import json
import shutil
import difflib

# Percorsi
json_path = "minions_bg.json"
source_dir = "static/images/downloaded"
dest_dir = "static/images/minions"

os.makedirs(dest_dir, exist_ok=True)

# Carica il JSON
with open(json_path, "r", encoding="utf-8") as f:
    minions = json.load(f)

def normalize(s):
    return s.lower().replace(" ", "").replace("'", "").replace(",", "").replace("!", "").replace("-", "").replace(".", "")

# Dizionari utili
id_to_name = {mid: data["name"] for mid, data in minions.items()}
normalized_names = {normalize(v): mid for mid, v in id_to_name.items()}

# Lista immagini
images = [f for f in os.listdir(source_dir) if f.lower().endswith((".png", ".jpg"))]

found = 0
missing = []

for img in images:
    name_no_ext = os.path.splitext(img)[0]
    norm_img = normalize(name_no_ext)

    # Trova nome più simile
    matches = difflib.get_close_matches(norm_img, normalized_names.keys(), n=1, cutoff=0.3)

    if matches:
        best_match = matches[0]
        card_id = normalized_names[best_match]
        dest_path = os.path.join(dest_dir, f"{card_id}.png")
        src_path = os.path.join(source_dir, img)

        shutil.copy(src_path, dest_path)
        found += 1
        print(f"✅ {img} → {card_id} ({id_to_name[card_id]})")
    else:
        missing.append(img)
        print(f"⚠️ Nessuna corrispondenza per {img}")

print(f"\nTotale immagini associate: {found}/{len(images)}")

if missing:
    with open("missing_images.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(missing))
    print("Lista delle immagini non trovate salvata in missing_images.txt")
