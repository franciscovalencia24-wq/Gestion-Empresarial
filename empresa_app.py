import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import tempfile
import subprocess
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de Página Streamlit
st.set_page_config(
    page_title="Gestión Empresarial - FV Asesorías",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prevenir que la traducción automática de Google Chrome rompa el DOM de React
st.markdown("""
<head>
    <meta name="google" content="notranslate">
</head>
<style>
    html { translate: no !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BASE DE DATOS Y CONEXIÓN CENTRALIZADA (data/crm_database.db)
# -----------------------------------------------------------------------------
sys.path.append(os.getcwd())
from src.database.connection import engine, SessionLocal, Base
from src.database.models import CompanyFinancialMovement, CompanyAccount

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

def normalize_period(per_raw, fecha_dt=None):
    if pd.notna(per_raw):
        s = str(per_raw).strip().replace("/", "-")
        parts = s.split("-")
        if len(parts) == 2 and len(parts[0]) == 4:
            month = parts[1].zfill(2)
            return f"{parts[0]}-{month}"
    if fecha_dt:
        return fecha_dt.strftime("%Y-%m")
    return None

def import_fv_excel(excel_path="REGISTRO FACTURAS.xlsx", company_name="FV Asesorías SpA"):
    if not os.path.exists(excel_path):
        return {"status": "error", "message": f"El archivo '{excel_path}' no se encuentra."}

    db = SessionLocal()
    try:
        try:
            xl = pd.ExcelFile(excel_path)
        except PermissionError:
            temp_path = os.path.join(tempfile.gettempdir(), "temp_registro_facturas.xlsx")
            subprocess.run(["powershell", "-Command", f"Copy-Item '{excel_path}' '{temp_path}' -Force"], check=True)
            xl = pd.ExcelFile(temp_path)

        db.query(CompanyFinancialMovement).filter(
            CompanyFinancialMovement.empresa == company_name,
            CompanyFinancialMovement.observaciones.like("Importado desde%")
        ).delete(synchronize_session=False)
        db.commit()

        if "DETALLE 26" in xl.sheet_names:
            df_det = xl.parse("DETALLE 26")
            
            # 1. ABONOS (Ingresos: Cols 0-7)
            for idx, row in df_det.iterrows():
                fecha_raw = row.iloc[0]
                folio_raw = row.iloc[1]
                concepto_raw = row.iloc[2]
                periodo_raw = row.iloc[3]
                neto_raw = row.iloc[5]
                iva_raw = row.iloc[6]
                total_raw = row.iloc[7]

                if pd.notna(total_raw) and isinstance(total_raw, (int, float)) and total_raw > 0:
                    concepto_str = str(concepto_raw).strip() if pd.notna(concepto_raw) else ""
                    if not concepto_str or concepto_str.upper() in ["FOLIO", "CONCEPTO", "TOTAL", "TOTALES"] or idx >= 58:
                        continue

                    fecha_dt = None
                    if pd.notna(fecha_raw):
                        try: fecha_dt = pd.to_datetime(fecha_raw).date()
                        except: pass
                    
                    periodo_str = normalize_period(periodo_raw, fecha_dt)
                    folio_str = str(int(folio_raw)) if pd.notna(folio_raw) and isinstance(folio_raw, (int, float)) else (str(folio_raw) if pd.notna(folio_raw) else None)

                    mov = CompanyFinancialMovement(
                        empresa=company_name,
                        tipo_movimiento="INGRESO",
                        categoria="FACTURACION / ABONO",
                        fecha=fecha_dt,
                        periodo=periodo_str,
                        folio_factura=folio_str,
                        concepto=concepto_str,
                        monto_neto=float(neto_raw) if pd.notna(neto_raw) and isinstance(neto_raw, (int, float)) else float(total_raw),
                        monto_iva=float(iva_raw) if pd.notna(iva_raw) and isinstance(iva_raw, (int, float)) else 0.0,
                        monto_total=float(total_raw),
                        cuenta_corriente="CTA. CTE. BCI: FV ASESORIAS",
                        observaciones="Importado desde DETALLE 26 (Abonos)"
                    )
                    db.add(mov)
                    added_count += 1

            # 2. EGRESOS (Gastos: Cols 9-16)
            for idx, row in df_det.iterrows():
                fecha_raw = row.iloc[9]
                proveedor_raw = row.iloc[11]
                detalle_raw = row.iloc[12]
                cuenta_raw = row.iloc[13]
                neto_raw = row.iloc[14]
                iva_raw = row.iloc[15]
                total_raw = row.iloc[16]

                if pd.notna(total_raw) and isinstance(total_raw, (int, float)) and total_raw > 0:
                    prov_str = str(proveedor_raw).strip() if pd.notna(proveedor_raw) else ""
                    if not prov_str or prov_str.upper() in ["PROVEEDOR", "TOTAL", "TOTALES"] or idx >= 58:
                        continue

                    fecha_dt = None
                    if pd.notna(fecha_raw):
                        try: fecha_dt = pd.to_datetime(fecha_raw).date()
                        except: pass
                    
                    periodo_str = normalize_period(None, fecha_dt)
                    det_str = str(detalle_raw).strip() if pd.notna(detalle_raw) else ""
                    cuenta_str = str(cuenta_raw).strip() if pd.notna(cuenta_raw) else "CTA. CTE. BCI: FV ASESORIAS"
                    concepto_full = f"{prov_str} - {det_str}".strip(" -")

                    cat = "GASTO / COMPRA"
                    prov_upper = prov_str.upper()
                    if "SUELDO" in prov_upper: cat = "SUELDO"
                    elif "PREVIRED" in prov_upper: cat = "PREVIRED"
                    elif "SII" in prov_upper or "IMPUESTO" in prov_upper: cat = "IMPUESTOS F29"
                    elif "ARRIENDO" in prov_upper: cat = "ARRIENDO"
                    elif "BOLETA" in prov_upper or "HONORARIO" in prov_upper: cat = "HONORARIOS"

                    mov = CompanyFinancialMovement(
                        empresa=company_name,
                        tipo_movimiento="EGRESO",
                        categoria=cat,
                        fecha=fecha_dt,
                        periodo=periodo_str,
                        razon_social=prov_str,
                        concepto=concepto_full,
                        monto_neto=float(neto_raw) if pd.notna(neto_raw) and isinstance(neto_raw, (int, float)) else float(total_raw),
                        monto_iva=float(iva_raw) if pd.notna(iva_raw) and isinstance(iva_raw, (int, float)) else 0.0,
                        monto_total=float(total_raw),
                        cuenta_corriente=cuenta_str,
                        observaciones="Importado desde DETALLE 26 (Egresos)"
                    )
                    db.add(mov)
                    added_count += 1

            # 3. MOVIMIENTOS SOCIOS (Cols 18-21)
            for idx, row in df_det.iterrows():
                if len(row) > 21:
                    fecha_raw = row.iloc[18]
                    concepto_raw = row.iloc[19]
                    cuenta_raw = row.iloc[20]
                    total_raw = row.iloc[21]

                    if pd.notna(total_raw) and isinstance(total_raw, (int, float)) and total_raw > 0:
                        conc_str = str(concepto_raw).strip() if pd.notna(concepto_raw) else ""
                        if not conc_str or conc_str.upper() in ["CONCEPTO", "TOTAL", "TOTALES"] or idx >= 58:
                            continue

                        fecha_dt = None
                        if pd.notna(fecha_raw):
                            try: fecha_dt = pd.to_datetime(fecha_raw).date()
                            except: pass

                        periodo_str = normalize_period(None, fecha_dt)
                        cuenta_str = str(cuenta_raw).strip() if pd.notna(cuenta_raw) else "CTA. CTE. BANCO CHILE: FCO"

                        socio_nombre = "FRANCISCO VALENCIA (SOCIO)"
                        if "NATALIA" in cuenta_str.upper() or "NATALIA" in conc_str.upper():
                            socio_nombre = "NATALIA TAPIA (SOCIA)"

                        tipo_mov = "MOVIMIENTO_CTA_CTE"
                        cat = "REEMBOLSO GASTO / COMPRA SOCIO"
                        conc_upper = conc_str.upper()

                        if "SUELDO" in conc_upper:
                            cat = "PAGO SUELDOS SOCIO"
                        elif "PRESTAMO" in conc_upper or "PRÉSTAMO" in conc_upper:
                            if "DEVOLUCION" in conc_upper or "DEVOLUCIÓN" in conc_upper:
                                tipo_mov = "DEVOLUCION_SOCIO"
                                cat = "DEVOLUCIÓN PRÉSTAMO SOCIO"
                            else:
                                tipo_mov = "PRESTAMO_SOCIO"
                                cat = "PRÉSTAMO A SOCIO"

                        mov = CompanyFinancialMovement(
                            empresa=company_name,
                            tipo_movimiento=tipo_mov,
                            categoria=cat,
                            fecha=fecha_dt,
                            periodo=periodo_str,
                            razon_social=socio_nombre,
                            concepto=conc_str,
                            monto_neto=float(total_raw),
                            monto_iva=0.0,
                            monto_total=float(total_raw),
                            cuenta_corriente=cuenta_str,
                            observaciones=f"Importado desde DETALLE 26 ({socio_nombre})"
                        )
                        db.add(mov)
                        added_count += 1

        db.commit()
        return {"status": "success", "message": f"Sincronizados {added_count} registros."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def fmt_money(val):
    if val is None or pd.isna(val): return "$ 0"
    return f"$ {val:,.0f}".replace(",", ".")

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO PRINCIPAL
# -----------------------------------------------------------------------------
from src.web.company_management_ui import render_company_management_ui

render_company_management_ui()

