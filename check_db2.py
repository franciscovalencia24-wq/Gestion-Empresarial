from src.database.connection import engine
import pandas as pd

df = pd.read_sql("SELECT id, rut, nombre, telefono, status_contacto FROM prospects WHERE nombre LIKE '%Sergio%'", con=engine)
print(df[df['telefono'].notna() & df['telefono'].str.contains('68453659', na=False, case=False, regex=False)])
