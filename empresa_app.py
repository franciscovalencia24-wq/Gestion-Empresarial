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

# -----------------------------------------------------------------------------
# BASE DE DATOS E INGESTION AUTOCONTENIDA (SQLite)
# -----------------------------------------------------------------------------
DB_PATH = "sqlite:///data/crm_database.db"
os.makedirs("data", exist_ok=True)
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
Base = declarative_base()

class CompanyFinancialMovement(Base):
    __tablename__ = 'company_financial_movements'
    id = Column(Integer, primary_base=True, primary_key=True, autoincrement=True)
    empresa = Column(String(100), default="FV Asesorías SpA")
    tipo_movimiento = Column(String(50)) # INGRESO, EGRESO, PRESTAMO_SOCIO, DEVOLUCION_SOCIO, MOVIMIENTO_CTA_CTE
    categoria = Column(String(100)) # FACTURACION, GASTO, PRÉSTAMO, etc.
    fecha = Column(Date)
    periodo = Column(String(20))
    folio_factura = Column(String(50))
    rut_contraparte = Column(String(20))
    razon_social = Column(String(200))
    concepto = Column(Text)
    monto_neto = Column(Float, default=0.0)
    monto_iva = Column(Float, default=0.0)
    monto_total = Column(Float, default=0.0)
    cuenta_corriente = Column(String(100))
    observaciones = Column(Text)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

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

        added_count = 0
        db.query(CompanyFinancialMovement).filter(CompanyFinancialMovement.empresa == company_name).delete()
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
st.markdown("""
<div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 16px; margin-bottom: 25px; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155;'>
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <div>
            <h1 style='color: #f8fafc; margin: 0; font-size: 2rem; font-weight: 800;'>🏢 Gestión Empresarial y Financiera</h1>
            <p style='color: #94a3b8; margin-top: 5px; margin-bottom: 0; font-size: 1rem;'>
                Control consolidado de facturación, egresos, préstamos a socios, cuentas corrientes e impuestos (F29) para <b>FV Asesorías</b> y <b>ALTUS</b>.
            </p>
        </div>
        <div style='background: rgba(255,255,255,0.08); padding: 10px 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: right;'>
            <span style='font-size: 0.8em; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.05em;'>Acceso Sincronizado</span><br/>
            <span style='font-weight: 700; color: #38bdf8;'>👥 Francisco Valencia & Natalia Tapia</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_emp, col_btn1, col_btn2 = st.columns([2, 1.2, 1.2])
with col_emp:
    empresa_sel = st.selectbox("🏢 Seleccionar Empresa:", ["FV Asesorías SpA", "ALTUS AI SpA (En constitución)"], index=0)

with col_btn1:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Sincronizar desde Excel", use_container_width=True):
        with st.spinner("Sincronizando REGISTRO FACTURAS.xlsx..."):
            res = import_fv_excel(company_name=empresa_sel)
            if res["status"] == "success":
                st.success(res["message"])
                st.rerun()
            else: st.error(res["message"])

with col_btn2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    show_new_form = st.checkbox("➕ Nuevo Movimiento")

db = SessionLocal()
try:
    movs = db.query(CompanyFinancialMovement).filter(
        CompanyFinancialMovement.empresa == empresa_sel
    ).order_by(CompanyFinancialMovement.fecha.desc()).all()

    # Si está vacía la BD en la nube, auto-importar desde Excel inmediatamente
    if not movs and os.path.exists("REGISTRO FACTURAS.xlsx"):
        import_fv_excel(company_name=empresa_sel)
        movs = db.query(CompanyFinancialMovement).filter(
            CompanyFinancialMovement.empresa == empresa_sel
        ).order_by(CompanyFinancialMovement.fecha.desc()).all()

    data_list = []
    for m in movs:
        data_list.append({
            "ID": m.id,
            "Tipo": m.tipo_movimiento,
            "Categoría": m.categoria or "GENERAL",
            "Fecha": m.fecha,
            "Período": m.periodo or "",
            "Folio": m.folio_factura or "",
            "RUT": m.rut_contraparte or "",
            "Razón Social / Proveedor": m.razon_social or "",
            "Concepto / Detalle": m.concepto or "",
            "Monto Neto": m.monto_neto or 0.0,
            "IVA": m.monto_iva or 0.0,
            "Monto Total": m.monto_total or 0.0,
            "Cuenta Corriente": m.cuenta_corriente or "CTA. CTE. BCI: FV ASESORIAS",
            "Observaciones": m.observaciones or ""
        })

    df_all = pd.DataFrame(data_list)
    if df_all.empty:
        df_all = pd.DataFrame(columns=[
            "ID", "Tipo", "Categoría", "Fecha", "Período", "Folio", "RUT",
            "Razón Social / Proveedor", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"
        ])

    df_ingresos = df_all[df_all["Tipo"] == "INGRESO"] if not df_all.empty else pd.DataFrame()
    df_egresos = df_all[df_all["Tipo"] == "EGRESO"] if not df_all.empty else pd.DataFrame()
    df_prestamos_otorgados = df_all[df_all["Tipo"] == "PRESTAMO_SOCIO"] if not df_all.empty else pd.DataFrame()
    df_devoluciones_socio = df_all[df_all["Tipo"] == "DEVOLUCION_SOCIO"] if not df_all.empty else pd.DataFrame()

    total_ingresos = df_ingresos["Monto Total"].sum() if not df_ingresos.empty else 0.0
    total_egresos = df_egresos["Monto Total"].sum() if not df_egresos.empty else 0.0
    utilidad_neta = total_ingresos - total_egresos
    prestamo_neto_socio = (df_prestamos_otorgados["Monto Total"].sum() if not df_prestamos_otorgados.empty else 0.0) - (df_devoluciones_socio["Monto Total"].sum() if not df_devoluciones_socio.empty else 0.0)
    saldo_bci_real = 24003331.0

    st.markdown("### 📊 Indicadores Financieros Consolidados y Conciliación Bancaria")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("🟢 Ingresos Ventas", fmt_money(total_ingresos))
    with k2: st.metric("🔴 Egresos Gastos", fmt_money(total_egresos))
    with k3: st.metric("💰 Utilidad Operacional", fmt_money(utilidad_neta))
    with k4: st.metric("🤝 Préstamo a Socio (Francisco Valencia)", fmt_money(prestamo_neto_socio))
    with k5: st.metric("🏦 Saldo Cta Cte BCI Real", fmt_money(saldo_bci_real))

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🟢 Facturas Emitidas / Abonos",
        "🔴 Facturas de Compra / Gastos",
        "🤝 Movimientos Cuentas Socios (Francisco & Natalia)",
        "🏛️ Estimación Impuestos F29",
        "🏦 Desglose por Cuentas Corrientes"
    ])

    with tab1:
        st.markdown("##### 🟢 Registro de Facturación Emitida e Ingresos")
        df_ing_view = df_ingresos.copy()
        if not df_ing_view.empty:
            df_ing_view["_folio_num"] = pd.to_numeric(df_ing_view["Folio"], errors="coerce").fillna(0)
            df_ing_view = df_ing_view.sort_values(by="_folio_num", ascending=False).drop(columns=["_folio_num"])
            st.dataframe(df_ing_view[["ID", "Fecha", "Período", "Folio", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"]], use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("##### 🔴 Registro de Facturas de Compra y Gastos")
        df_egr_view = df_egresos.copy()
        if not df_egr_view.empty:
            st.dataframe(df_egr_view[["ID", "Fecha", "Período", "Categoría", "RUT", "Razón Social / Proveedor", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"]], use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("##### 🤝 Registro de Cuentas Corrientes y Movimientos de Socios")
        df_socio_all = df_all[df_all["Tipo"].isin(["PRESTAMO_SOCIO", "DEVOLUCION_SOCIO", "MOVIMIENTO_CTA_CTE"])].copy()
        if not df_socio_all.empty:
            st.dataframe(df_socio_all[["ID", "Fecha", "Razón Social / Proveedor", "Categoría", "Concepto / Detalle", "Cuenta Corriente", "Monto Total", "Observaciones"]], use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("##### 🏛️ Detalle Impuestos F29 por Período")
        if not df_all.empty and "Período" in df_all.columns:
            df_valid = df_all[df_all["Período"].str.contains(r"^\d{4}-\d{2}$", na=False)]
            if not df_valid.empty:
                df_f29 = df_valid.groupby(["Período", "Tipo"])["IVA"].sum().unstack(fill_value=0).reset_index()
                if "INGRESO" not in df_f29.columns: df_f29["INGRESO"] = 0.0
                if "EGRESO" not in df_f29.columns: df_f29["EGRESO"] = 0.0
                df_f29["Impuesto IVA a Pagar"] = df_f29["INGRESO"] - df_f29["EGRESO"]
                st.dataframe(df_f29, use_container_width=True, hide_index=True)

    with tab5:
        st.markdown("##### 🏦 Desglose de Movimientos por Cuenta Corriente")
        if not df_all.empty:
            df_cta = df_all.groupby(["Cuenta Corriente", "Tipo"])["Monto Total"].sum().unstack(fill_value=0).reset_index()
            st.dataframe(df_cta, use_container_width=True, hide_index=True)

finally:
    db.close()
