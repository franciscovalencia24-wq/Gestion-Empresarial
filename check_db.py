from src.database.connection import engine
import pandas as pd

df = pd.read_sql("SELECT id, rut, nombre, telefono, status_contacto FROM prospects WHERE telefono LIKE '%68453659%'", con=engine)
print(df)
