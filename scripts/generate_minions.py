import requests
import json
import os

URL = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "minions_bg.json")

response = requests.get(URL)
data = response.json()

bg_minions = {}

for card in data:
    if card.get("isBattlegroundsPoolMinion") and card.get("type") == "MINION":
        code = card["id"]
        bg_minions[code] = {
            "name": card.get("name"),
            "type": card.get("race", ""),
            "effect": card.get("text", ""),
            "attack": card.get("attack", 0),
            "health": card.get("health", 0),
            "cost": card.get("cost", 0),
            "techLevel": card.get("techLevel", 0),
            "image": f"https://d15f34w2p8l1cc.cloudfront.net/hearthstone/{card.get('id')}.png"
        }

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(bg_minions, f, ensure_ascii=False, indent=2)

print(f"[✅] {len(bg_minions)} minion salvati in {OUTPUT_FILE}")
