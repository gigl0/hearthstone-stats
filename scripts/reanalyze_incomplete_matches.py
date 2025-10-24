import os
import xml.etree.ElementTree as ET
from datetime import datetime
from app.db.session import SessionLocal
from app.models.models import BattlegroundsMatch
from app.services.bg_importer_enhanced import HERO_DATA, MINION_DATA
from rich import print

XML_FILE = os.path.expandvars(r"%APPDATA%\HearthstoneDeckTracker\BgsLastGames.xml")


def _parse_time(t: str):
    if not t:
        return None
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


def reanalyze_incomplete_matches():
    """Rileggi i match incompleti e aggiorna dal file XML."""
    if not os.path.exists(XML_FILE):
        print(f"[red]❌ File XML non trovato: {XML_FILE}[/red]")
        return

    session = SessionLocal()
    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    matches = session.query(BattlegroundsMatch).filter(
        (BattlegroundsMatch.placement == None)
        | (BattlegroundsMatch.placement == 0)
        | (BattlegroundsMatch.game_result == "unknown")
        | (BattlegroundsMatch.minions_count == 0)
    ).all()

    if not matches:
        print("[green]✅ Nessun match incompleto trovato.[/green]")
        session.close()
        return

    print(f"[yellow]🧩 Trovati {len(matches)} match da correggere...[/yellow]")

    fixed = 0
    for m in matches:
        # cerca il game corrispondente nel file XML (entro ±10 secondi)
        game_found = None
        for g in root.findall("Game"):
            xml_start = g.get("StartTime")
            if not xml_start:
                continue

            try:
                xml_dt = datetime.fromisoformat(xml_start.replace("Z", "+00:00"))
            except Exception:
                continue

            if m.start_time and abs((xml_dt - m.start_time).total_seconds()) < 10:
                game_found = g
                break

        if not game_found:
            print(f"[grey]⚠️ Nessun match trovato per {m.hero_name} ({m.start_time})[/grey]")
            continue

        game = game_found

        # Placement
        placement = (
            game.get("Placement")
            or game.get("Placemenent")  # typo possibile nel file XML
            or game.get("FinalPlacement")
        )
        placement = int(placement) if placement and placement.isdigit() else None

        # Rating
        rating = int(float(game.get("Rating") or 0))
        rating_after = int(float(game.get("RatingAfter") or 0))
        rating_delta = rating_after - rating

        # Hero
        hero_id = game.get("Hero")
        hero_info = HERO_DATA.get(hero_id, {"name": hero_id, "image": ""})
        hero_name = hero_info.get("name", hero_id)
        hero_image = hero_info.get("image", "")

        # Minions
        final_board = game.find("FinalBoard")
        minions, minion_names, minion_types, minion_images = [], [], [], []
        if final_board is not None:
            for minion in final_board.findall("Minion"):
                card = minion.find("CardId")
                if card is not None and card.text:
                    cid = card.text.strip().upper().replace("_G", "")
                    info = MINION_DATA.get(cid, {})
                    minions.append({
                        "id": cid,
                        "name": info.get("name", cid),
                        "type": info.get("type", ""),
                        "image": info.get("image", "")
                    })
                    minion_names.append(info.get("name", cid))
                    if info.get("type"):
                        minion_types.append(info["type"])
                    if info.get("image"):
                        minion_images.append(info["image"])

        # Game result
        if placement == 1:
            result = "win"
        elif placement and 2 <= placement <= 4:
            result = "top4"
        elif placement:
            result = "loss"
        else:
            result = "unknown"

        # Aggiornamento nel DB
        m.placement = placement
        m.rating = rating
        m.rating_after = rating_after
        m.rating_delta = rating_delta
        m.game_result = result
        m.hero = hero_id
        m.hero_name = hero_name
        m.hero_image = hero_image
        m.minions = minions
        m.minions_count = len(minions)
        m.minions_list = ", ".join(minion_names)
        m.minion_types = ", ".join(sorted(set(minion_types)))
        m.minion_images = "|".join(minion_images)

        session.add(m)
        fixed += 1
        print(f"[cyan]🔁 Aggiornato {hero_name} → placement {placement}, {len(minions)} minion[/cyan]")

    session.commit()
    session.close()
    print(f"[bold green]✅ Correzione completata: {fixed} match aggiornati.[/bold green]")


if __name__ == "__main__":
    reanalyze_incomplete_matches()
