import sqlite3
import pandas as pd
con = sqlite3.connect('data/processed/prospectos.db')
try:
    df = pd.read_sql("SELECT nombre FROM prospects WHERE rut = '9536620-1'", con)
    print("SUCCESS:", df.iloc[0]['nombre'])
except Exception as e:
    print("ERROR:", e)
