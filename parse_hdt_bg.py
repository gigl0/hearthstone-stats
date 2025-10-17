import xml.etree.ElementTree as ET
import csv

# Nome del file di log HDT BG
input_file = "BgsLastGames.xml"
output_file = "parsed_games.csv"

# Parsing XML
tree = ET.parse(input_file)
root = tree.getroot()

# Lista per salvare le partite
games_data = []

for game in root.findall('Game'):
    player_id = game.get('Player')
    hero = game.get('Hero')
    start_time = game.get('StartTime')
    end_time = game.get('EndTime')
    placement = game.get('Placemenent')  # HDT a volte ha typo
    rating = game.get('Rating')
    rating_after = game.get('RatingAfter')
    
    # Lista dei minion (solo CardId)
    minions = []
    final_board = game.find('FinalBoard')
    if final_board is not None:
        for minion in final_board.findall('Minion'):
            card_id = minion.find('CardId').text
            minions.append(card_id)
    
    games_data.append({
        "player_id": player_id,
        "hero": hero,
        "start_time": start_time,
        "end_time": end_time,
        "placement": placement,
        "rating": rating,
        "rating_after": rating_after,
        "minions": ";".join(minions)
    })

# Scrittura CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["player_id", "hero", "start_time", "end_time", "placement", "rating", "rating_after", "minions"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(games_data)

print(f"Parsing completato! {len(games_data)} partite salvate in '{output_file}'")
