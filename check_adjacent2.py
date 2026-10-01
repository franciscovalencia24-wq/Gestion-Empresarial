from src.database.connection import engine
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
df = pd.read_sql("SELECT id, rut, nombre, telefono, status_contacto FROM prospects WHERE id BETWEEN 1378 AND 1385", con=engine)
print(df)
