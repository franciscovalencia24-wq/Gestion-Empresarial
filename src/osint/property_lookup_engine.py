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

        comuna_upper = str(comuna or "").upper().strip()
        destino_upper = str(destino or "").upper().strip()

        # Multiplicador base por comuna (default: 1.85)
        mult_comuna = self.COMUNA_MULTIPLIERS.get(comuna_upper, 1.85)
        
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

        # Simulación / Consulta de catastro oficial indexado por RUT
        results = self._query_sii_catastro_database(rut_clean, nombre_cliente)
        
        for prop in results:
            avaluo = float(prop.get("Avalúo Fiscal (CLP)", 0.0))
            comuna = prop.get("Comuna", "SANTIAGO")
            destino = prop.get("Destino", "HABITACIONAL")
            
            # Asignar valor comercial estimado en UF si viene en 0
            if not prop.get("Valor Com. (UF)") or prop.get("Valor Com. (UF)") == 0.0:
                prop["Valor Com. (UF)"] = self.estimate_commercial_value_uf(avaluo, comuna, destino)
                
        return results

    def _query_sii_catastro_database(self, rut_clean, nombre_cliente):
        """
        Consulta la base catastral nacional por RUT.
        (Retorna lista vacía por defecto si no hay sesión de scraping web activa)
        """
        # La consulta por web scraping real se ejecuta al conectar las credenciales SII / API
        return []

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
