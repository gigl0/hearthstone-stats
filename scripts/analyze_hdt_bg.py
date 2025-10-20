import pandas as pd
from pathlib import Path
import json

# === Percorsi file ===
ROOT = Path(__file__).parent.parent
INPUT_CSV = ROOT / "parsed_games_clean.csv"
OUTPUT_JSON = ROOT / "stats_summary.json"

def analyze_battlegrounds():
    print("📊 Analisi dati Battlegrounds in corso...")

    # === 1️⃣ Caricamento ===
    df = pd.read_csv(INPUT_CSV)
    print(f"✅ Caricate {len(df)} partite da {INPUT_CSV.name}")

    # === 2️⃣ Pulizia base ===
    df = df.dropna(subset=["hero_name", "placement"])
    df["placement"] = pd.to_numeric(df["placement"], errors="coerce")
    df["rating_delta"] = pd.to_numeric(df["rating_delta"], errors="coerce")
    df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")

    # === 3️⃣ Statistiche globali ===
    total_games = len(df)
    win_rate = (df["game_result"] == "win").mean() * 100
    top4_rate = df["game_result"].isin(["win", "top4"]).mean() * 100
    avg_duration = df["duration_min"].mean()
    avg_rating_delta = df["rating_delta"].mean()

    global_stats = {
        "total_games": total_games,
        "win_rate": round(win_rate, 2),
        "top4_rate": round(top4_rate, 2),
        "avg_duration_min": round(avg_duration, 1),
        "avg_rating_delta": round(avg_rating_delta, 1),
    }

    # === 4️⃣ Statistiche per eroe ===
    hero_stats = (
        df.groupby("hero_name")
        .agg(
            games=("hero_name", "count"),
            win_rate=("game_result", lambda x: (x == "win").mean() * 100),
            top4_rate=("game_result", lambda x: x.isin(["win", "top4"]).mean() * 100),
            avg_placement=("placement", "mean"),
            avg_rating_delta=("rating_delta", "mean"),
        )
        .reset_index()
        .sort_values(by="win_rate", ascending=False)
    )

    # === 5️⃣ Statistiche per tipo di minion ===
    # Ogni riga può avere più tipi separati da ", "
    minion_stats = {}
    for _, row in df.iterrows():
        types = str(row.get("minion_types", "")).split(", ")
        for t in [x for x in types if x]:
            if t not in minion_stats:
                minion_stats[t] = {"games": 0, "wins": 0, "top4s": 0}
            minion_stats[t]["games"] += 1
            if row["game_result"] == "win":
                minion_stats[t]["wins"] += 1
            if row["game_result"] in ["win", "top4"]:
                minion_stats[t]["top4s"] += 1

    for t, d in minion_stats.items():
        d["win_rate"] = round(d["wins"] / d["games"] * 100, 2)
        d["top4_rate"] = round(d["top4s"] / d["games"] * 100, 2)

    # === 6️⃣ Esporta risultati ===
    output_data = {
        "global": global_stats,
        "by_hero": hero_stats.to_dict(orient="records"),
        "by_minion_type": minion_stats,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"💾 Risultati salvati in {OUTPUT_JSON}")
    print("✅ Analisi completata.")

if __name__ == "__main__":
    analyze_battlegrounds()
