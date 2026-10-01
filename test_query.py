import pandas as pd
from src.database.connection import engine
df = pd.read_sql("SELECT * FROM prospects WHERE (status_contacto != 'Descartado' OR status_contacto IS NULL) AND es_cliente = 1 AND telefono IS NOT NULL AND nombre IS NOT NULL AND telefono != 'None' AND nombre != 'None'", con=engine)
print("Length:", len(df))
print(df[['id', 'nombre', 'supervisor']])
