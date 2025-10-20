import pandas as pd
import sqlite3

df = pd.read_csv("app/data/parsed_games_clean.csv")
conn = sqlite3.connect("app/data/bgs.db")
df.to_sql("matches", conn, if_exists="replace", index=False)
conn.close()
