import pandas as pd
import os
import sys
import logging
from datetime import datetime

sys.path.append(os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement

logger = logging.getLogger("sii_importer")

def auto_categorize_compra(razon_social: str) -> str:
    """Aplica heurísticas a la razón social para deducir la categoría. Retorna ⚠️ CLASIFICAR GASTO si falla."""
    if not razon_social:
        return "⚠️ CLASIFICAR GASTO"
    
    razon = str(razon_social).upper()
    if "SUELDO" in razon: return "SUELDO"
    if "PREVIRED" in razon: return "PREVIRED"
    if "SII" in razon or "IMPUESTO" in razon or "TESORERIA" in razon: return "IMPUESTOS F29"
    if "ARRIENDO" in razon: return "ARRIENDO"
    if "HONORARIO" in razon or "BOLETA" in razon: return "HONORARIOS"
    
    return "⚠️ CLASIFICAR GASTO"

def process_sii_dataframe(df: pd.DataFrame, company_name: str, filename_context: str = ""):
    """
    Procesa un dataframe parseado de un CSV del SII (Compras o Ventas)
    y los inserta a SQLite sin duplicar facturas.
    """
    db = SessionLocal()
    added_count = 0
    skipped_count = 0

    try:
        # Detectar si es Compra o Venta por el nombre de las columnas
        cols_upper = [str(c).upper() for c in df.columns]
        
        is_venta = any("RUT CLIENTE" in c for c in cols_upper)
        is_compra = any("RUT PROVEEDOR" in c for c in cols_upper)

        if not is_venta and not is_compra:
            return {"status": "error", "message": f"El archivo {filename_context} no parece ser un archivo válido del SII (Faltan columnas de RUT Cliente o Proveedor)."}

        for idx, row in df.iterrows():
            # Extraer Folio para validar
            def get_val(keywords):
                for kw in keywords:
                    for col in df.columns:
                        if kw in str(col).upper():
                            return row[col]
                return None
            
            folio_raw = get_val(["FOLIO"])
            if pd.isna(folio_raw) or str(folio_raw).strip() == "":
                continue # Sin folio no es una factura válida
            folio_str = str(int(folio_raw)) if isinstance(folio_raw, (int, float)) else str(folio_raw).strip()

            rut_contraparte = str(get_val(["RUT CLIENTE", "RUT PROVEEDOR"]) or "").strip()
            razon_social = str(get_val(["RAZON SOCIAL"]) or "").strip()
            fecha_raw = get_val(["FECHA DOCTO"])
            
            neto_raw = get_val(["MONTO NETO"])
            iva_raw = get_val(["MONTO IVA RECUPERABLE", "MONTO IVA"])
            total_raw = get_val(["MONTO TOTAL"])

            if pd.isna(total_raw):
                continue
            try:
                total_val = float(total_raw)
                neto_val = float(neto_raw) if pd.notna(neto_raw) else total_val
                iva_val = float(iva_raw) if pd.notna(iva_raw) else 0.0
            except ValueError:
                continue
            
            if total_val <= 0:
                continue

            fecha_dt = None
            periodo_str = ""
            if pd.notna(fecha_raw):
                try:
                    fecha_dt = datetime.strptime(str(fecha_raw).split(" ")[0], "%d/%m/%Y").date()
                    periodo_str = fecha_dt.strftime("%Y-%m")
                except Exception:
                    pass

            if not fecha_dt:
                fecha_dt = datetime.today().date()
                periodo_str = fecha_dt.strftime("%Y-%m")

            if is_venta:
                tipo_mov = "INGRESO"
                cat = "FACTURACION / ABONO"
                concepto = f"Factura Venta - {razon_social}"
            else:
                tipo_mov = "EGRESO"
                cat = auto_categorize_compra(razon_social)
                concepto = f"Factura Compra - {razon_social}"

            # REGLA ANTI-DUPLICADOS (Conflicto robusto)
            # Para evitar duplicar facturas anteriores (que a veces venían sin RUT),
            # cruzamos por empresa, tipo, folio y monto total.
            existe = db.query(CompanyFinancialMovement).filter(
                CompanyFinancialMovement.empresa == company_name,
                CompanyFinancialMovement.tipo_movimiento == tipo_mov,
                CompanyFinancialMovement.folio_factura == folio_str,
                CompanyFinancialMovement.monto_total == total_val
            ).first()

            if existe:
                # Si existe, podríamos actualizar el RUT si faltaba
                if not existe.rut_contraparte and rut_contraparte:
                    existe.rut_contraparte = rut_contraparte
                if existe.observaciones and "DETALLE 26" in existe.observaciones:
                    pass # Preservamos la observacion antigua
                skipped_count += 1
                continue
            
            new_mov = CompanyFinancialMovement(
                empresa=company_name,
                tipo_movimiento=tipo_mov,
                categoria=cat,
                fecha=fecha_dt,
                periodo=periodo_str,
                folio_factura=folio_str,
                rut_contraparte=rut_contraparte,
                razon_social=razon_social,
                concepto=concepto,
                monto_neto=neto_val,
                monto_iva=iva_val,
                monto_total=total_val,
                cuenta_corriente="CTA. CTE. BCI: FV ASESORIAS",
                observaciones="Importado desde SII RCV"
            )
            db.add(new_mov)
            added_count += 1

        db.commit()
        return {
            "status": "success", 
            "message": f"{filename_context} procesado: {added_count} nuevos, {skipped_count} omitidos (duplicados)."
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error procesando dataframe del SII {filename_context}: {e}")
        return {"status": "error", "message": f"Error interno CSV {filename_context}: {str(e)}"}
    finally:
        db.close()
