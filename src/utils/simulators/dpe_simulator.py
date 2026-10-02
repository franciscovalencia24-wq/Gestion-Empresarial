import os
import tempfile
import json
import google.genai as genai

class DPESimulator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            # We don't raise an error here to prevent breaking if not using file parsing
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.5-pro'

    def calcular_beneficio_deposito_convenido(self, renta_bruta_mensual: float, valor_uf: float = 38000.0) -> dict:
        """
        Calcula el impacto y ahorro tributario por Depósito Convenido (DPE) 
        asumiendo que el ejecutivo optimiza parte de su renta.
        Tope anual es 900 UF.
        """
        try:
            renta_anual = renta_bruta_mensual * 12
            tope_anual_clp = 900 * valor_uf
            
            # Asumimos que si la renta es muy alta, el cliente puede aportar hasta un 15% de su renta o el tope de 900 UF
            aporte_sugerido = min(renta_anual * 0.15, tope_anual_clp)
            
            # Tramo marginal estimado simple para calcular el ahorro directo (Art 42 LIR)
            tramo_estimado = 0.0
            if renta_anual > 120000000: tramo_estimado = 0.40
            elif renta_anual > 80000000: tramo_estimado = 0.35
            elif renta_anual > 50000000: tramo_estimado = 0.304
            elif renta_anual > 30000000: tramo_estimado = 0.23
            else: tramo_estimado = 0.135
            
            ahorro_fiscal_estimado = aporte_sugerido * tramo_estimado
            
            return {
                "aporte_dpe_sugerido": aporte_sugerido,
                "ahorro_fiscal_dpe": ahorro_fiscal_estimado,
                "tramo_utilizado": tramo_estimado * 100
            }
        except Exception as e:
            return {
                "aporte_dpe_sugerido": 0.0,
                "ahorro_fiscal_dpe": 0.0,
                "tramo_utilizado": 0.0,
                "error": str(e)
            }

    def analyze_file(self, file_bytes, file_name, tope_imponible_uf=84.3, valor_uf=38000):
        try:
            file_uri = None
            content_payload = []
            
            prompt = """
            Eres un experto analista de datos. Este es un 'Certificado de Cotizaciones Obligatorias' de una AFP chilena.
            Tu tarea es transcribir TODAS las filas de cotizaciones históricas individuales que aparecen en el documento. No importa si hay 1 o 10 empleadores, quiero TODAS las filas de pago.
            
            Reglas estrictas:
            1. Extrae ABSOLUTAMENTE TODAS las filas de la tabla de cotizaciones, desde la primera hasta la última página.
            2. Devuelve estrictamente un JSON con esta estructura plana:
            {
                "filas_extraidas": [
                    {"periodo": "MM-YYYY", "rut_pagador": "12345678-9", "renta_imponible": 2500000, "monto_cotizacion_obligatoria": 250000}
                ]
            }
            IMPORTANTE:
            - IGNORA POR COMPLETO cualquier fila que diga "Total", "Subtotal", "Total del Mes" o similares. SOLO extrae los pagos individuales de los empleadores. Extraer totales duplicará falsamente los montos.
            - Si el certificado muestra explícitamente una columna de 'Renta Imponible' o 'Remuneración Imponible', extrae ese valor numérico en "renta_imponible".
            - Si el certificado muestra el "Monto" pagado (la cotización), extráelo en "monto_cotizacion_obligatoria".
            - Ambos valores deben ser numéricos enteros (sin puntos ni símbolo $). Si alguno no está en el documento, pon 0.
            - NO omitas ningún mes, transcribe todo el historial completo.
            """

            ext = file_name.lower().split('.')[-1]
            use_gemini = True
            raw_json = "{}"
            raw_json_2 = "{}"

            if ext == 'pdf':
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                
                # Intentar parseo matemático nativo primero
                try:
                    import pdfplumber
                    import re
                    native_filas = []
                    
                    with pdfplumber.open(tmp_path) as pdf:
                        for page in pdf.pages:
                            tables = page.extract_tables()
                            if tables:
                                for table in tables:
                                    for r in table:
                                        if r and len(r) >= 7 and r[0] and re.match(r"^\d{2}/\d{4}$", str(r[0]).strip()):
                                            periodo = str(r[0]).strip().replace('/', '-')
                                            tipo = str(r[1]).replace('\n', ' ').lower()
                                            monto_str = str(r[3]).replace('$', '').replace('.', '').strip()
                                            renta_str = str(r[5]).replace('$', '').replace('.', '').strip()
                                            
                                            rut1 = str(r[6]).replace('.', '').strip()
                                            rut2 = str(r[7]).replace('-', '').strip() if len(r) > 7 and r[7] else ""
                                            rut = f"{rut1}-{rut2}" if rut2 else rut1
                                            
                                            if 'obligatoria' in tipo or 'cotizacion' in tipo:
                                                monto_val = int(monto_str) if monto_str.isdigit() else 0
                                                renta_val = int(renta_str) if renta_str.isdigit() else 0
                                                if renta_val > 0 or monto_val > 0:
                                                    native_filas.append({
                                                        "periodo": periodo,
                                                        "rut_pagador": rut,
                                                        "renta_imponible": renta_val,
                                                        "monto_cotizacion_obligatoria": monto_val
                                                    })
                            
                    if len(native_filas) > 0:
                        use_gemini = False
                        raw_json = json.dumps({"filas_extraidas": native_filas})
                        raw_json_2 = raw_json
                except Exception as e:
                    import logging
                    logging.warning(f"Error en parseo nativo: {e}")
                
                if use_gemini:
                    file_uri = self.client.files.upload(file=tmp_path)
                    content_payload = [file_uri, prompt]
            elif ext in ['xlsx', 'xls']:
                import io
                import pandas as pd
                df = pd.read_excel(io.BytesIO(file_bytes), header=None)
                csv_text = df.to_csv(index=False)
                content_payload = [f"A continuación los datos extraídos del archivo Excel en formato CSV:\n\n{csv_text}\n\n", prompt]
            elif ext == 'csv':
                csv_text = file_bytes.decode('utf-8', errors='ignore')
                content_payload = [f"A continuación los datos del archivo CSV:\n\n{csv_text}\n\n", prompt]
            else:
                return {"success": False, "error": f"Formato no soportado: {ext}"}
            
            if use_gemini:
                import concurrent.futures
                
                def call_model(temp):
                    return self.client.models.generate_content(
                        model=self.model_name,
                        contents=content_payload,
                        config=genai.types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=temp
                        )
                    ).text
                
                if ext == 'pdf':
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        future1 = executor.submit(call_model, 0.0)
                        future2 = executor.submit(call_model, 0.1)
                        raw_json = future1.result()
                        raw_json_2 = future2.result()
                else:
                    raw_json = call_model(0.0)
                    raw_json_2 = raw_json
                
                if file_uri:
                    self.client.files.delete(name=file_uri.name)
            
            def parse_json_robust(text):
                try:
                    return json.loads(text)
                except Exception as e:
                    import re
                    import logging
                    logging.warning(f"Error parseando JSON ({e}), usando fallback regex.")
                    filas = []
                    # Extrae cada objeto dentro del array que contenga "periodo"
                    matches = re.findall(r'\{[^{}]*"periodo"[^{}]*\}', text)
                    for m in matches:
                        try:
                            m_clean = re.sub(r',\s*\}', '}', m)
                            fila = json.loads(m_clean)
                            filas.append(fila)
                        except:
                            pass
                    return {"filas_extraidas": filas}
                    
            data = parse_json_robust(raw_json)
            data2 = parse_json_robust(raw_json_2)
            
            sum1 = sum(f.get("monto_cotizacion_obligatoria", f.get("renta_imponible", 0)) for f in data.get("filas_extraidas", []))
            sum2 = sum(f.get("monto_cotizacion_obligatoria", f.get("renta_imponible", 0)) for f in data2.get("filas_extraidas", []))
            
            cross_validation_warning = (sum1 != sum2) and ext == 'pdf'
            
            TOPE_IMPONIBLE_HISTORICO = {
                2019: 79.3,
                2020: 80.2,
                2021: 81.6,
                2022: 81.6,
                2023: 81.6,
                2024: 84.3,
                2025: 84.3,
                2026: 84.3
            }
            
            def get_uf_value(periodo):
                import calendar
                try:
                    month, year = map(int, periodo.split('-'))
                    if len(str(year)) == 2:
                        year += 2000
                    last_day = calendar.monthrange(year, month)[1]
                    
                    uf_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uf_historica.json")
                    with open(uf_file_path, "r", encoding="utf-8") as f:
                        uf_data = json.load(f)
                    
                    for d in range(last_day, 0, -1):
                        test_date = f"{year}-{month:02d}-{d:02d}"
                        if test_date in uf_data:
                            return uf_data[test_date]
                except Exception:
                    pass
                return 38000.0
                
            meses_con_exceso = []
            total_exceso = 0
            
            filas = data.get("filas_extraidas", [])
            
            # Primero agrupar por periodo y rut para obtener la renta máxima 
            # (para evitar duplicaciones de SIS, Cotización Adicional, etc.)
            max_renta_por_empleador = {}
            for fila in filas:
                periodo = fila.get("periodo")
                renta = fila.get("renta_imponible", 0)
                cotizacion = fila.get("monto_cotizacion_obligatoria", 0)
                rut = fila.get("rut_pagador", "Desconocido")
                
                # Heurística matemática para AFP Capital y similares
                if renta == 0 and cotizacion > 0:
                    renta = cotizacion * 10
                        
                # Si la IA extrajo el mismo valor en ambos campos (error común de tablas)
                if renta > 0 and renta == cotizacion:
                    if cotizacion < 400000:
                        renta = cotizacion * 10
                
                if not periodo or "-" not in str(periodo):
                    continue
                    
                key = (periodo, rut)
                if key not in max_renta_por_empleador:
                    max_renta_por_empleador[key] = 0
                
                if renta > max_renta_por_empleador[key]:
                    max_renta_por_empleador[key] = renta
                    
            agrupado = {}
            for (periodo, rut), max_renta in max_renta_por_empleador.items():
                if periodo not in agrupado:
                    agrupado[periodo] = {"renta_total": 0, "empleadores": set()}
                
                agrupado[periodo]["renta_total"] += max_renta
                agrupado[periodo]["empleadores"].add(rut)
            
            from datetime import datetime
            current_date = datetime.now()
            
            # Calcular excesos dinámicamente (Límite legal: 60 meses hacia atrás / 5 años)
            for periodo, info in agrupado.items():
                renta_total = info["renta_total"]
                
                try:
                    month, year = map(int, periodo.split('-'))
                    if len(str(year)) == 2:
                        year += 2000
                        
                    # Límite de 60 meses
                    period_date = datetime(year, month, 1)
                    months_diff = (current_date.year - period_date.year) * 12 + (current_date.month - period_date.month)
                    if months_diff > 60:
                        continue # Prescrito por ley (más de 5 años)
                except:
                    year = 2024
                    
                tope_uf_legal = TOPE_IMPONIBLE_HISTORICO.get(year, 84.3)
                uf_dia = get_uf_value(periodo)
                tope_imponible_clp = tope_uf_legal * uf_dia
                
                if renta_total > tope_imponible_clp:
                    exceso_renta = renta_total - tope_imponible_clp
                    exceso_cotizacion = exceso_renta * 0.10
                    total_exceso += exceso_cotizacion
                    
                    meses_con_exceso.append({
                        "periodo": periodo,
                        "cantidad_empleadores": len(info["empleadores"]),
                        "renta_total": renta_total,
                        "tope_aplicado": tope_imponible_clp,
                        "uf_utilizada": uf_dia,
                        "exceso_renta": exceso_renta,
                        "devolucion_estimada": exceso_cotizacion
                    })
                    
            return {
                "success": True,
                "total_devolucion_estimada": total_exceso,
                "meses_analizados": len(agrupado),
                "meses_con_exceso": meses_con_exceso,
                "cross_validation_warning": cross_validation_warning,
                "raw_json": raw_json
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
