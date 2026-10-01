import os
import sqlite3
import pandas as pd

def main():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "osint_mass_tracker.db")
    if not os.path.exists(db_path):
        print("No se encontró la base de datos de seguimiento.")
        return
        
    conn = sqlite3.connect(db_path)
    
    # Extraer todos los descartados
    query = """
    SELECT filepath, status, processed_at
    FROM processed_files
    WHERE status LIKE 'SKIPPED%' OR status = 'EMPTY_TEXT'
    ORDER BY processed_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No hay archivos descartados registrados.")
        return
        
    # Extraer la carpeta de origen (ej: ALIRO, MALENTIN KARIME) para categorizarlos
    def extract_campaign(path):
        parts = path.split(os.sep)
        try:
            # Assuming structure like C:\Users\franc\OneDrive\Documentos\<CAMPAIGN>\...
            idx = parts.index("Documentos")
            return parts[idx+1] if len(parts) > idx+1 else "Desconocido"
        except:
            return "Desconocido"
            
    df['Campaña/Carpeta'] = df['filepath'].apply(extract_campaign)
    
    # Crear enlace clickeable para Excel
    df['Abrir Archivo'] = df['filepath'].apply(lambda x: f'=HYPERLINK("{x}", "Abrir Documento")')
    
    # Reordenar columnas
    df = df[['Campaña/Carpeta', 'filepath', 'Abrir Archivo', 'status', 'processed_at']]
    df.columns = ['Carpeta de Origen', 'Ruta Completa', 'Acción', 'Motivo del Descarte', 'Fecha de Procesamiento']
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reporte_Archivos_Descartados.xlsx")
    
    # Guardar a Excel con un poco de formato
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Descartados')
    
    workbook = writer.book
    worksheet = writer.sheets['Descartados']
    
    # Ajustar el ancho de las columnas
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 70)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 25)
    
    writer.close()
    
    print(f"Reporte generado exitosamente en: {output_path}")
    print(f"Total de archivos descartados encontrados: {len(df)}")
    
if __name__ == "__main__":
    main()
