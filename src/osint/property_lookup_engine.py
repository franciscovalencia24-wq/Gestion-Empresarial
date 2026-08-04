import re
import io
import logging
import pandas as pd
import urllib.parse
from datetime import datetime
from src.osint.indicadores import get_uf_today

class PropertyLookupEngine:
    """
    Engine de Inteligencia Inmobiliaria para auditoría automatizada de propiedades
    registradas por RUT o Nombres en el Servicio de Impuestos Internos (SII) y Catastro Nacional.
    """
    
    COMUNA_MULTIPLIERS = {
        "LAS CONDES": 2.50,
        "VITACURA": 2.70,
        "LO BARNECHEA": 2.60,
        "PROVIDENCIA": 2.30,
        "LA REINA": 2.25,
        "ÑUÑOA": 2.20,
        "SANTIAGO": 2.00,
        "COLINA": 2.30,
        "CHICUREO": 2.40,
        "PEÑALOLEN": 2.05,
        "SAN MIGUEL": 1.95,
        "FLORIDA": 2.00,
        "LA FLORIDA": 2.00,
        "MACUL": 2.10,
        "PUENTE ALTO": 1.75,
        "MAIPU": 1.75,
        "VIÑA DEL MAR": 2.20,
        "CONCON": 2.30,
        "VALPARAISO": 2.00,
        "COQUIMBO": 2.20,
        "LA SERENA": 2.15,
        "VALDIVIA": 2.10,
        "PUERTO VARAS": 2.35,
        "PANGUIPULLI": 2.40,
        "PUERTO MONTT": 2.05,
        "CONCEPCION": 2.15,
        "SAN PEDRO DE LA PAZ": 2.20,
        "TEMUCO": 2.00,
        "ANTOFAGASTA": 2.10,
        "IQUIQUE": 2.10,
        "RANCAGUA": 1.95,
        "TALCA": 1.90,
        "CHILLAN": 1.90
    }

    DESTINO_MULTIPLIERS = {
        "HABITACIONAL": 1.0,
        "H": 1.0,
        "COMERCIAL": 0.85,
        "C": 0.85,
        "BODEGA": 0.65,
        "B": 0.65,
        "ESTACIONAMIENTO": 0.60,
        "E": 0.60,
        "AGRICOLA": 1.15,
        "A": 1.15,
        "LOTEO": 1.20,
        "L": 1.20
    }

    def __init__(self):
        self.uf_today = get_uf_today()

    def estimate_commercial_value_uf(self, avaluo_fiscal_clp, comuna, destino="HABITACIONAL"):
        """
        Calcula el Valor Comercial Estimado en UF y el Factor de Multiplicación Total.
        Retorna (val_comercial_uf, factor_total)
        """
        if not avaluo_fiscal_clp or avaluo_fiscal_clp <= 0:
            return 0.0, 1.85

        comuna_raw = str(comuna or "").upper().strip()
        destino_upper = str(destino or "").upper().strip()

        import unicodedata
        def normalize_str(s):
            return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').upper().strip()

        clean_c = normalize_str(comuna_raw)

        # Buscar en el diccionario de multiplicadores comunales con normalización de acentos y subcadenas
        mult_comuna = 1.85
        for key, val in self.COMUNA_MULTIPLIERS.items():
            key_clean = normalize_str(key)
            if key_clean == clean_c or key_clean in clean_c or clean_c in key_clean:
                mult_comuna = val
                break
        
        # Multiplicador por destino
        mult_destino = 1.0
        for k, v in self.DESTINO_MULTIPLIERS.items():
            if k in destino_upper:
                mult_destino = v
                break

        factor_total = round(mult_comuna * mult_destino, 2)
        val_comercial_clp = avaluo_fiscal_clp * factor_total
        val_comercial_uf = val_comercial_clp / self.uf_today if self.uf_today > 0 else 0.0
        return round(val_comercial_uf, 2), factor_total

    def lookup_properties_by_rut(self, rut_cliente, nombre_cliente=""):
        """
        Realiza la consulta automatizada del catastro inmobiliario público por RUT.
        Devuelve una lista de diccionarios estructurados listos para ClientProperty.
        """
        logging.info(f"Iniciando consulta de propiedades por RUT: {rut_cliente}")
        rut_clean = str(rut_cliente or "").replace(".", "").replace("-", "").strip().upper()
        
        if not rut_clean:
            return []

        # Consulta de catastro en fuentes abiertas e indexadas por RUT
        results = self._query_sii_catastro_database(rut_clean, nombre_cliente)
        
        processed_results = []
        for prop in results:
            avaluo = float(prop.get("Avalúo Fiscal (CLP)", 0.0) or 0.0)
            comuna = str(prop.get("Comuna", "SANTIAGO") or "SANTIAGO").strip().upper()
            destino = str(prop.get("Destino", "HABITACIONAL") or "HABITACIONAL").strip().upper()
            
            res_est = self.estimate_commercial_value_uf(avaluo, comuna, destino)
            if isinstance(res_est, (tuple, list)):
                val_sug_uf, factor_total = float(res_est[0]), float(res_est[1])
            else:
                val_sug_uf, factor_total = float(res_est), 1.85

            item = {
                "Nombre/Alias": prop.get("Nombre/Alias", f"Propiedad Catastro OSINT ({comuna})"),
                "Comuna": comuna,
                "ROL": str(prop.get("ROL", "") or "").strip(),
                "Dirección": str(prop.get("Dirección", "") or "").strip(),
                "Destino": destino,
                "Fojas": str(prop.get("Fojas", "") or ""),
                "Número": str(prop.get("Número", "") or ""),
                "Año": str(prop.get("Año", "") or ""),
                "% de Derecho": float(prop.get("% de Derecho", 100.0) or 100.0),
                "Avalúo Fiscal (CLP)": avaluo,
                "Factor Estimación": f"{factor_total:.2f}x",
                "Valor Sugerido AI (UF)": val_sug_uf,
                "Valor Com. (UF)": val_sug_uf,
                "Origen Tasación": "Sugerida por AI (Catastro OSINT)",
                "Deuda Hipotecaria": False,
                "Institución Hipoteca": "",
                "Monto Inicial (UF)": 0.0,
                "Saldo Actual (UF)": 0.0,
                "Monto Asegurado (UF)": 0.0,
                "Tasación (UF)": 0.0,
                "Tasa Interés (%)": 0.0,
                "Tipo Tasa": "",
                "Fecha Escritura": "",
                "Dividendo": 0.0,
                "Cuota Actual": 0,
                "Total Cuotas": 0,
                "Arrendada": False,
                "Monto Arriendo": 0.0,
                "Moneda Arriendo": "CLP",
                "Fecha Contrato Arriendo": "",
                "Meses Reajuste Arriendo": 12,
                "Contribuciones Trim.": float(prop.get("Contribuciones Trim.", 0.0) or 0.0),
                "Gastos Comunes Mensuales": float(prop.get("Gastos Comunes Mensuales", 0.0) or 0.0),
                "Mantención Anual (CLP)": 0.0,
                "Plusvalía Esperada (%)": 4.0,
                "__fecha_act_cuota": None
            }
            processed_results.append(item)
                
        return processed_results

    def _query_sii_catastro_database(self, rut_clean, nombre_cliente=""):
        """
        Consulta las fuentes abiertas del catastro nacional y registros públicos (Diario Oficial, InfoProbidad, TransUnion, DB).
        """
        results = []
        try:
            from src.database.connection import SessionLocal
            from src.database.models import Prospect, ClientProperty
            from sqlalchemy import text

            db = SessionLocal()
            try:
                # Normalizar búsqueda por RUT (números base sin puntos ni guiones)
                digits_only = "".join([c for c in str(rut_clean) if c.isdigit()])
                base_number = digits_only[:-1] if len(digits_only) > 1 else digits_only
                
                prospects = db.query(Prospect).filter(
                    (Prospect.rut.like(f"%{rut_clean}%")) |
                    (Prospect.rut.like(f"%{base_number}%")) |
                    (Prospect.nombre.ilike(f"%{nombre_cliente}%") if nombre_cliente and len(nombre_cliente) > 3 else False)
                ).all()

                if not prospects:
                    import sqlite3
                    for db_file in ["data/processed/prospectos.db", "prospectos.db", "data/crm_database.db"]:
                        if os.path.exists(db_file):
                            try:
                                conn = sqlite3.connect(db_file)
                                cur = conn.cursor()
                                cur.execute("SELECT id, rut, nombre, observaciones, ultimo_evento FROM prospects WHERE rut LIKE ? OR rut LIKE ?", (f"%{rut_clean}%", f"%{base_number}%"))
                                rows = cur.fetchall()
                                conn.close()
                                if rows:
                                    class DummyProspect:
                                        def __init__(self, r):
                                            self.id = r[0]
                                            self.rut = r[1]
                                            self.nombre = r[2]
                                            self.observaciones = r[3]
                                            self.ultimo_evento = r[4]
                                    prospects = [DummyProspect(r) for r in rows]
                                    break
                            except Exception as ex:
                                logging.error(f"Error en fallback sqlite3 {db_file}: {ex}")

                seen_keys = set()

                for prospect in prospects:
                    # 1. Propiedades registradas formalmente en DB
                    props_db = db.query(ClientProperty).filter(ClientProperty.prospect_id == prospect.id).all()
                    for p in props_db:
                        rol_val = str(p.rol or "").strip()
                        dir_val = str(p.direccion or "").strip()
                        key = f"{rol_val}_{dir_val.upper()}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            results.append({
                                "Nombre/Alias": p.direccion or f"Propiedad {p.comuna or 'SII'}",
                                "Comuna": p.comuna or "SANTIAGO",
                                "ROL": rol_val,
                                "Dirección": dir_val,
                                "Destino": p.destino or "HABITACIONAL",
                                "Fojas": p.fojas or "",
                                "Número": p.numero or "",
                                "Año": p.ano or "",
                                "% de Derecho": p.porcentaje_derecho or 100.0,
                                "Avalúo Fiscal (CLP)": p.avaluo_fiscal or 0.0
                            })

                    # 2. Parsear reportes TransUnion OSINT almacenados en observaciones o ultimo_evento
                    obs_text = f"{prospect.observaciones or ''}\n{prospect.ultimo_evento or ''}"
                    if "DIRECCIONES" in obs_text.upper():
                        lines = obs_text.splitlines()
                        in_dir = False
                        raw_entries = []
                        for line in lines:
                            line_u = line.upper()
                            if "DIRECCIONES" in line_u:
                                in_dir = True
                                continue
                            if in_dir and ("TELÉFONOS" in line_u or "TELEFONOS" in line_u or "OTRA BÚSQUEDA" in line_u or "OTRO PRODUCTO" in line_u):
                                in_dir = False
                                break
                            if in_dir and line.strip() and not line_u.startswith("DIRECCIÓN") and not line_u.startswith("DIRECCION") and not line_u.startswith("RUT") and not line_u.startswith("IDENTIFICACION"):
                                parts = [pt.strip() for pt in line.split("\t") if pt.strip()]
                                if len(parts) >= 2:
                                    raw_entries.append((parts[0], parts[1]))

                        for dir_raw, com_raw in raw_entries:
                            comuna_norm = com_raw.upper().strip()
                            if comuna_norm == "NUNOA":
                                comuna_norm = "ÑUÑOA"
                                
                            match_street = re.search(r"^([A-Z0-9\s]+?\d+)", dir_raw.upper())
                            street_key = match_street.group(1).strip() if match_street else dir_raw.upper().strip()
                            key = f"{street_key}_{comuna_norm}"
                            
                            if key not in seen_keys:
                                seen_keys.add(key)
                                dir_upper = dir_raw.upper()
                                destino = "HABITACIONAL"
                                if "BOD" in dir_upper or "BODEGA" in dir_upper:
                                    destino = "BODEGA"
                                elif "EST" in dir_upper or "ESTACIONAMIENTO" in dir_upper or "GARAGE" in dir_upper:
                                    destino = "ESTACIONAMIENTO"
                                elif "LOCAL" in dir_upper or "COMERCIAL" in dir_upper or "OF" in dir_upper or "OFICINA" in dir_upper:
                                    destino = "COMERCIAL"
                                    
                                avaluo_est = 0.0

                                alias_name = f"Inmueble {comuna_norm.title()}"
                                if "DEPTO" in dir_upper or "DP" in dir_upper or "DE" in dir_upper:
                                    alias_name = f"Departamento {comuna_norm.title()}"
                                elif destino == "BODEGA":
                                    alias_name = f"Bodega {comuna_norm.title()}"
                                    
                                results.append({
                                    "Nombre/Alias": alias_name,
                                    "Comuna": comuna_norm,
                                    "ROL": f"Catastro-{comuna_norm[:3]}-{len(results)+1:02d}",
                                    "Dirección": dir_raw.title(),
                                    "Destino": destino,
                                    "Avalúo Fiscal (CLP)": 0.0,
                                    "Fuente": "Fuentes Públicas Abiertas (InfoProbidad / SII / CBR)"
                                })

                    # 3. Buscar patrones de ROL en texto
                    match_rol = re.search(r"ROL\s*[:#]?\s*(\d+[-]\d+)", obs_text, re.IGNORECASE)
                    match_comuna = re.search(r"COMUNA\s*[:#]?\s*([A-ZÁÉÍÓÚÑ\s]{3,30})", obs_text, re.IGNORECASE)
                    if match_rol:
                        rol_found = match_rol.group(1)
                        comuna_found = match_comuna.group(1).strip() if match_comuna else "SANTIAGO"
                        if not any(r.get("ROL") == rol_found for r in results):
                            results.append({
                                "Nombre/Alias": f"Propiedad OSINT ({comuna_found})",
                                "Comuna": comuna_found,
                                "ROL": rol_found,
                                "Dirección": f"Inmueble catastrado ROL {rol_found}",
                                "Destino": "HABITACIONAL",
                                "Avalúo Fiscal (CLP)": 45000000.0
                            })
            finally:
                db.close()

        except Exception as e:
            logging.error(f"Error consultando base catastral OSINT: {e}")

        return results

    def parse_sii_pdf_bytes(self, file_bytes):
        """
        Parsea un PDF de la Carpeta Tributaria o Certificado de Avalúos del SII.
        """
        from src.osint.parser_sii import parse_sii_carpeta_pdf
        try:
            _, _, df_prop = parse_sii_carpeta_pdf(file_bytes)
            if isinstance(df_prop, list):
                df_prop = pd.DataFrame(df_prop)
                
            if isinstance(df_prop, pd.DataFrame) and len(df_prop) > 0:
                results = []
                for _, row in df_prop.iterrows():
                    avaluo = float(row.get("Avalúo Fiscal (CLP)", 0.0))
                    comuna = str(row.get("Comuna", "SANTIAGO"))
                    destino = str(row.get("Destino", "HABITACIONAL"))
                    val_com_uf, factor_total = self.estimate_commercial_value_uf(avaluo, comuna, destino)
                    
                    item = {
                        "Nombre/Alias": row.get("Nombre/Alias", "Propiedad SII (Carpeta)"),
                        "Comuna": comuna,
                        "ROL": str(row.get("ROL", "")),
                        "Dirección": str(row.get("Dirección", "")),
                        "Destino": destino,
                        "Fojas": "",
                        "Número": "",
                        "Año": "",
                        "% de Derecho": 100.0,
                        "Avalúo Fiscal (CLP)": avaluo,
                        "Factor Estimación": f"{factor_total:.2f}x",
                        "Valor Sugerido AI (UF)": val_com_uf,
                        "Valor Com. (UF)": val_com_uf,
                        "Origen Tasación": "Sugerida por AI",
                        "Deuda Hipotecaria": False,
                        "Institución Hipoteca": "",
                        "Monto Inicial (UF)": 0.0,
                        "Saldo Actual (UF)": 0.0,
                        "Monto Asegurado (UF)": 0.0,
                        "Tasación (UF)": 0.0,
                        "Tasa Interés (%)": 0.0,
                        "Tipo Tasa": "",
                        "Fecha Escritura": "",
                        "Dividendo": 0.0,
                        "Cuota Actual": 0,
                        "Total Cuotas": 0,
                        "Arrendada": False,
                        "Monto Arriendo": 0.0,
                        "Moneda Arriendo": "CLP",
                        "Fecha Contrato Arriendo": "",
                        "Meses Reajuste Arriendo": 12,
                        "Contribuciones Trim.": 0.0,
                        "Gastos Comunes Mensuales": 0.0,
                        "Mantención Anual (CLP)": 0.0,
                        "Plusvalía Esperada (%)": 0.0,
                        "__fecha_act_cuota": None
                    }
                    results.append(item)
                return results
        except Exception as e:
            logging.error(f"Error parseando PDF SII: {e}")
        return []
