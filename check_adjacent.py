from src.database.connection import engine
import pandas as pd

df = pd.read_sql("SELECT id, rut, nombre, telefono, status_contacto FROM prospects WHERE id BETWEEN 1378 AND 1385", con=engine)
print(df)
