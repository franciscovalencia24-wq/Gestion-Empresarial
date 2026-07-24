import pandas as pd
import io

def parse_cmf_deudas_csv(file_bytes, filename=""):
    """
    Parsea el informe de deudas de la CMF en formato CSV o Excel (.xls / .xlsx).
    Retorna un DataFrame con las columnas mapeadas para la BD.
    """
    try:
        df = pd.DataFrame()
        # 1. Intentar lectura como Excel si la extensión es xls/xlsx o si falla csv
        if filename.lower().endswith('.xls') or filename.lower().endswith('.xlsx'):
            try:
                df = pd.read_excel(io.BytesIO(file_bytes))
            except Exception:
                pass

        if df.empty:
            # 2. Intentar lectura CSV con distintas codificaciones
            encodings_to_try = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python', encoding=enc)
                    if not df.empty and len(df.columns) > 3:
                        break
                except Exception:
                    continue

        if df.empty:
            return pd.DataFrame()

        # Normalizar nombres de columnas
        cols = []
        for c in df.columns:
            c_str = str(c).upper().replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Á", "A").replace("É", "E")
            if "INSTITU" in c_str: cols.append("INSTITUCION")
            elif "TIPO DE CR" in c_str or "TIPO CR" in c_str: cols.append("TIPO_CREDITO")
            elif "CARGA FINANCIERA" in c_str: cols.append("CARGA_FINANCIERA")
            elif "MONTO ORIGINAL" in c_str: cols.append("MONTO_ORIGINAL")
            elif "MONTO ACTUAL" in c_str: cols.append("MONTO_ACTUAL")
            elif "MORA ACTUAL" in c_str: cols.append("MORA_ACTUAL")
            elif "OTORGAMIENTO" in c_str: cols.append("FECHA_OTORGAMIENTO")
            elif "VENCIMIENTO" in c_str: cols.append("FECHA_VENCIMIENTO")
            else: cols.append(c_str)

        df.columns = cols

        def clean_str(val):
            if pd.isna(val): return ""
            s = str(val).strip()
            # Arreglar tildes corruptos de latin1/cp1252
            s = s.replace("Ita", "Itaú").replace("Ita", "Itaú").replace("crdito", "crédito").replace("Crdito", "Crédito").replace("Lnea", "Línea").replace("lnea", "línea")
            return s

        def clean_num(val):
            if pd.isna(val): return 0.0
            try:
                s = str(val).replace('$', '').replace('.', '').replace(',', '.').strip()
                return float(s)
            except:
                return 0.0

        result_list = []
        for _, row in df.iterrows():
            institucion = clean_str(row.get("INSTITUCION"))
            tipo = clean_str(row.get("TIPO_CREDITO"))

            monto_original = clean_num(row.get("MONTO_ORIGINAL"))
            monto_actual = clean_num(row.get("MONTO_ACTUAL"))
            carga_financiera = clean_num(row.get("CARGA_FINANCIERA"))
            mora_actual = clean_num(row.get("MORA_ACTUAL"))

            if monto_actual > 0 or mora_actual > 0 or monto_original > 0:
                result_list.append({
                    "Institucion": institucion,
                    "Tipo_Credito": tipo,
                    "Monto Original": monto_original,
                    "Monto Actual": monto_actual,
                    "Carga Financiera": carga_financiera,
                    "Mora": mora_actual,
                    "Otorgamiento": clean_str(row.get("FECHA_OTORGAMIENTO")),
                    "Vencimiento": clean_str(row.get("FECHA_VENCIMIENTO")),
                    "Observaciones": ""
                })

        return pd.DataFrame(result_list)

    except Exception as e:
        print(f"Error parsing CMF Deudas file: {e}")
        return pd.DataFrame()

