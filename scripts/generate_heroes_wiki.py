import requests, json
from pathlib import Path

URL = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
OUTPUT = Path(__file__).parent.parent / "heroes_bg.json"

def generate_heroes_from_api():
    print("📥 Fetching heroes from HearthstoneJSON API...")
    data = requests.get(URL).json()
    heroes = {}
    for card in data:
        if card.get("type") == "HERO" and card.get("set") == "BATTLEGROUNDS":
            heroes[card["id"]] = {
                "name": card["name"],
                "image": f"https://art.hearthstonejson.com/v1/render/latest/enUS/512x/{card['id']}.png",
                "dbfId": card.get("dbfId"),
            }
    print(f"✅ Found {len(heroes)} heroes.")
    OUTPUT.write_text(json.dumps(heroes, indent=2, ensure_ascii=False))
    print(f"💾 Saved to {OUTPUT}")

if __name__ == "__main__":
    generate_heroes_from_api()
