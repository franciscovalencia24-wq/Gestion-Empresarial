import sqlite3
import pandas as pd

con = sqlite3.connect('prospectos.db')
df = pd.read_sql("SELECT id, nombre, score_liquidez FROM prospects WHERE id LIKE 'DO%' ORDER BY score_liquidez DESC LIMIT 5", con=con)
print(df)
