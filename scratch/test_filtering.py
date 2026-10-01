import sqlite3, pandas as pd
con = sqlite3.connect('data/crm_database.db')
sql = "SELECT * FROM prospects WHERE status_contacto != 'Contactado' AND (status_contacto != 'Descartado' OR status_contacto IS NULL) AND es_cliente = 1 AND telefono IS NOT NULL AND nombre IS NOT NULL AND telefono != 'None' AND nombre != 'None'"
df = pd.read_sql(sql, con=con)
print('Total rows:', len(df))

# Simulamos los filtros
cols_a_estandarizar = ['ciudad', 'nombre_asesor', 'supervisor', 'tipo_negocio', 'origen_info', 'titulo_profesional']
for col in cols_a_estandarizar:
    if col in df.columns:
        df[col] = df[col].apply(lambda c: str(c).strip().title() if pd.notna(c) and str(c).strip() else None)

valencia = df[df['nombre'].str.contains('VALENCIA', na=False, case=False)]
print("Is Valencia in df after standardization?")
print(valencia[['rut', 'nombre', 'ciudad', 'nombre_asesor', 'supervisor']])

def get_mask_except():
    mask = pd.Series(True, index=df.index)
    # asumiendo ningun filtro
    return mask

filtered_df = df[get_mask_except()].copy()
print("Total filtered:", len(filtered_df))
print(filtered_df[['rut', 'nombre', 'ciudad', 'nombre_asesor', 'supervisor']].to_string())
