import pandas as pd
import numpy as np

def parse_sura_excel(file_path, sheet_name='18.03.25', rut_mapping=None):
    """
    Lee y limpia el archivo Excel, separando carteras dinámicamente según rut_mapping.
    rut_mapping format: { "77.039.670-0": "Empresa", "7.431.527-5": "Persona Natural" }
    """
    try:
        # 1. Cargar el archivo Excel
        # Intentamos primero con la hoja específica, si falla leemos la primera
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except ValueError:
            df = pd.read_excel(file_path)
            
        # 2. Limpiar nombres de columnas (eliminar espacios extras)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Eliminar filas donde 'PRODUCTO' es nulo y 'RUT' también
        df = df.dropna(subset=['PRODUCTO', 'TOTAL COMPRA'], how='all').reset_index(drop=True)
        
        # 3. Forward fill para RUT, NOMBRE y REGIMEN
        if 'RUT' in df.columns:
            df['RUT'] = df['RUT'].ffill()
        if 'NOMBRE' in df.columns:
            df['NOMBRE'] = df['NOMBRE'].ffill()
        if 'REGIMEN' in df.columns:
            df['REGIMEN'] = df['REGIMEN'].ffill()
            
        # 4. Limpieza de columnas numéricas
        numeric_cols = ['N° CUOTAS', 'PRECIO COMPRA', 'TOTAL COMPRA', 'VALOR ACTUAL', 'TOTAL ACTUALIZADO', 'RENTABILIDAD']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace(['-', ' '], np.nan), errors='coerce')
                
        # 5. Filtrar filas válidas que tengan un producto y un total actualizado
        df = df.dropna(subset=['PRODUCTO', 'TOTAL ACTUALIZADO'])
        
        # Diccionario para agrupar las carteras
        carteras = {}
        
        # 6. Separar las carteras usando rut_mapping
        if rut_mapping is None:
            # Comportamiento por defecto (compatibilidad hacia atrás)
            rut_mapping = {
                '77.039.670-0': 'Empresa',
                '7.431.527-5': 'Persona Natural'
            }
            
        # 7. Motor Inteligente de Asignación de Series (SURA)
        def asignar_serie_sura(row, is_apv, aum_total):
            prod = str(row['PRODUCTO']).strip()
            if "SURA" not in prod.upper():
                return prod
                
            # Limpiar serie anterior si existe
            if prod.endswith(" E") or prod.endswith(" F") or prod.endswith(" APV") or prod.endswith(" A"):
                prod = prod.rsplit(' ', 1)[0]
                
            if is_apv:
                return f"{prod} APV"
            else:
                if aum_total >= 150000000:
                    return f"{prod} F"
                else:
                    return f"{prod} E"
                    
        # Iteramos sobre el DataFrame para crear las agrupaciones
        ruts_en_df = df['RUT'].unique() if 'RUT' in df.columns else []
        
        for rut in ruts_en_df:
            tipo = rut_mapping.get(rut, "Persona Natural") # Por defecto asumimos Persona Natural
            
            df_rut = df[df['RUT'] == rut].copy()
            
            if tipo == "Empresa":
                key = f"empresa_{rut}"
                aum_total = df_rut['TOTAL ACTUALIZADO'].sum()
                df_rut['PRODUCTO'] = df_rut.apply(lambda r: asignar_serie_sura(r, False, aum_total), axis=1)
                carteras[key] = df_rut
                
            elif tipo == "Persona Natural":
                # Si es Persona Natural, separamos por APV y General
                is_apv = df_rut['REGIMEN'].str.contains('APV', na=False, case=False) if 'REGIMEN' in df_rut.columns else pd.Series(False, index=df_rut.index)
                
                df_apv = df_rut[is_apv].copy()
                df_general = df_rut[~is_apv].copy()
                
                if not df_apv.empty:
                    df_apv['PRODUCTO'] = df_apv.apply(lambda r: asignar_serie_sura(r, True, 0), axis=1)
                    carteras[f"persona_apv_{rut}"] = df_apv
                    
                if not df_general.empty:
                    aum_total = df_general['TOTAL ACTUALIZADO'].sum()
                    df_general['PRODUCTO'] = df_general.apply(lambda r: asignar_serie_sura(r, False, aum_total), axis=1)
                    carteras[f"persona_general_{rut}"] = df_general
                    
        # Reconstruir dataframe combinado
        df_combined = pd.concat(carteras.values()) if carteras else df
        carteras["raw_cleaned"] = df_combined
        
        return carteras
        
    except Exception as e:
        print(f"Error parseando el archivo: {e}")
        return None

if __name__ == "__main__":
    file_path = "Resumen Actualizado Inversiones ARANDA_AUDILEX 18-03-25.xlsx"
    print("Iniciando Ingesta de Excel SURA...")
    resultados = parse_sura_excel(file_path)
    
    if resultados:
        print("\\n--- RESUMEN DE CARTERAS INGERIDAS ---")
        for key, df_subset in resultados.items():
            if key != "raw_cleaned":
                print(f"Bolsa: {key} - {len(df_subset)} instrumentos - AUM: ${df_subset['TOTAL ACTUALIZADO'].sum():,.0f}")
