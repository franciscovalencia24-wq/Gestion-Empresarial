import sqlite3
import pandas as pd
con = sqlite3.connect('data/processed/prospectos.db')
try:
    df = pd.read_sql("SELECT * FROM prospects", con)
    print("SUCCESS: Read all rows without crash.")
except Exception as e:
    print("ERROR:", e)
