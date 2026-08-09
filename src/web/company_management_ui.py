import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())
from src.database.connection import SessionLocal
from src.database.models import CompanyFinancialMovement, CompanyAccount
from src.ingestion.excel_importer_fv import import_fv_excel

def fmt_money(val):
    if val is None or pd.isna(val):
        return "$ 0"
    return f"$ {val:,.0f}".replace(",", ".")

def render_company_management_ui():
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

    # 1. SELECCIÓN DE EMPRESA Y ACCIONES SUPERIORES
    col_emp, col_btn1, col_btn2 = st.columns([2, 1.2, 1.2])

    with col_emp:
        empresa_sel = st.selectbox(
            "🏢 Seleccionar Empresa:",
            ["FV Asesorías SpA", "ALTUS AI SpA (En constitución)"],
            index=0,
            key="company_sel_main"
        )

    with col_btn1:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Sincronizar desde Excel", use_container_width=True, type="secondary"):
            with st.spinner("Sincronizando REGISTRO FACTURAS.xlsx..."):
                res = import_fv_excel(company_name=empresa_sel)
                if res["status"] == "success":
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res["message"])

    with col_btn2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        show_new_form = st.checkbox("➕ Nuevo Movimiento", key="toggle_new_mov")

    # 0. DESCARGA AUTOMÁTICA DESDE GOOGLE CLOUD STORAGE EN NUBE
    if "gcs_db_synced" not in st.session_state:
        try:
            from src.utils.gcs_sync import download_db_from_gcs
            download_db_from_gcs()
            st.session_state["gcs_db_synced"] = True
        except Exception:
            pass

    # 2. CARGA DE DATOS DESDE BASE DE DATOS Y AUTO-CREACIÓN DE TABLAS Y COLUMNAS SQLITE
    from sqlalchemy import text
    from src.database.connection import SessionLocal, engine, Base
    
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    db = SessionLocal()
    for col_sql in [
        "ALTER TABLE company_financial_movements ADD COLUMN monto_exento FLOAT DEFAULT 0.0",
        "ALTER TABLE company_financial_movements ADD COLUMN created_at DATETIME"
    ]:
        try:
            db.execute(text(col_sql))
            db.commit()
        except Exception:
            db.rollback()

    # Auto-asegurar que el préstamo de $2.500.000 a Natalia Tapia (28.07.2026) exista siempre en la BD
    try:
        check_nat = db.query(CompanyFinancialMovement).filter(
            CompanyFinancialMovement.tipo_movimiento == "PRESTAMO_SOCIO",
            CompanyFinancialMovement.razon_social.contains("NATALIA"),
            CompanyFinancialMovement.monto_total == 2500000.0
        ).first()
        if not check_nat:
            mov_nat = CompanyFinancialMovement(
                empresa=empresa_sel,
                tipo_movimiento="PRESTAMO_SOCIO",
                categoria="PRESTAMO SOCIO",
                fecha=datetime(2026, 7, 28).date(),
                periodo="2026-07",
                rut_contraparte="",
                razon_social="NATALIA TAPIA (SOCIA)",
                concepto="Préstamo a Socia Natalia Tapia",
                monto_neto=2500000.0,
                monto_iva=0.0,
                monto_total=2500000.0,
                cuenta_corriente="CTA. CTE. BCI: FV ASESORIAS",
                observaciones="Registrado manualmente desde Dashboard Web"
            )
            db.add(mov_nat)
            db.commit()
    except Exception:
        db.rollback()

    try:
        if "FV" in empresa_sel:
            movs = db.query(CompanyFinancialMovement).filter(
                CompanyFinancialMovement.empresa.like("%FV%")
            ).order_by(CompanyFinancialMovement.fecha.desc()).all()
        else:
            movs = db.query(CompanyFinancialMovement).filter(
                CompanyFinancialMovement.empresa.like("%ALTUS%")
            ).order_by(CompanyFinancialMovement.fecha.desc()).all()

        data_list = []
        for m in movs:
            neto_v = round(float(m.monto_neto or 0.0))
            iva_v = round(float(m.monto_iva or 0.0))
            total_v = round(float(m.monto_total or 0.0))
            if total_v == 0 and (neto_v > 0 or iva_v > 0):
                total_v = neto_v + iva_v

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
                "Monto Neto": neto_v,
                "IVA": iva_v,
                "Monto Total": total_v,
                "Cuenta Corriente": m.cuenta_corriente or "CTA. CTE. BCI: FV ASESORIAS",
                "Observaciones": m.observaciones or ""
            })

        df_all = pd.DataFrame(data_list)
        if df_all.empty:
            df_all = pd.DataFrame(columns=[
                "ID", "Tipo", "Categoría", "Fecha", "Período", "Folio", "RUT",
                "Razón Social / Proveedor", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"
            ])

        # FORMULARIO NUEVO MOVIMIENTO (INTERACTIVO Y REACTIVO EN TIEMPO REAL)
        if show_new_form:
            with st.expander("📝 Formulario de Registro Manual de Movimiento", expanded=True):
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    n_tipo = st.selectbox("Tipo de Movimiento", ["EGRESO", "INGRESO", "PRESTAMO_SOCIO", "DEVOLUCION_SOCIO", "MOVIMIENTO_CTA_CTE"], key="n_mov_tipo")
                    n_categoria = st.selectbox("Categoría", ["ARRIENDO", "GASTO / COMPRA", "FACTURACION / ABONO", "PRÉSTAMO A SOCIO", "DEVOLUCIÓN PRÉSTAMO SOCIO", "REEMBOLSO GASTO / COMPRA SOCIO", "PAGO SUELDOS SOCIO", "IMPUESTOS F29", "OTROS"], key="n_mov_cat")
                    n_fecha = st.date_input("Fecha", value=datetime.today(), key="n_mov_fecha")

                with fc2:
                    n_folio = st.text_input("N° Factura / Folio", value="", key="n_mov_folio")
                    n_rut = st.text_input("RUT Contraparte / Proveedor", value="", key="n_mov_rut")
                    n_razon_opt = st.selectbox("Socio / Proveedor / Entidad", [
                        "OTRO PROVEEDOR / ENTIDAD (ej: Arriendo Oficina / Inmobiliaria)",
                        "FRANCISCO VALENCIA (SOCIO)",
                        "NATALIA TAPIA (SOCIA)"
                    ], key="n_mov_razon_opt")
                    if "OTRO" in n_razon_opt:
                        n_razon = st.text_input("Nombre Razón Social / Proveedor", value="Inmobiliaria / Pago Arriendo", key="n_mov_razon_txt")
                    else:
                        n_razon = n_razon_opt

                with fc3:
                    n_concepto = st.text_input("Concepto / Detalle", value="Pago de Arriendo Oficina", key="n_mov_concepto")
                    
                    # MONTO NETO CON MOSTRADOR EN TIEMPO REAL
                    default_neto = 200000 if n_categoria == "ARRIENDO" else 0
                    n_neto = st.number_input(
                        "Monto Neto ($)",
                        min_value=0,
                        value=default_neto,
                        step=10000,
                        format="%d",
                        key="n_neto_input_val",
                        help="Monto en pesos chilenos sin decimales"
                    )
                    
                    # CASILLA CASILLA PARA CALCULAR IVA (19%) AUTOMÁTICAMENTE
                    n_calc_iva = st.checkbox(
                        "☑️ Calcular IVA (19%) automáticamente",
                        value=False,
                        key="n_chk_calc_iva_auto",
                        help="Marca esta casilla si la factura o gasto incluye 19% IVA afecto. Déjala desmarcada para Arriendos u Honorarios Exentos."
                    )
                    
                    if n_calc_iva:
                        auto_iva = int(round(n_neto * 0.19))
                        n_iva = st.number_input(
                            f"Monto IVA (19%) ➔ {fmt_money(auto_iva)}",
                            min_value=0,
                            value=auto_iva,
                            step=1000,
                            format="%d",
                            key="n_iva_val_auto"
                        )
                    else:
                        n_iva = st.number_input(
                            f"Monto IVA ($) ➔ {fmt_money(0)}",
                            min_value=0,
                            value=0,
                            step=1000,
                            format="%d",
                            key="n_iva_val_manual"
                        )

                    # ETIQUETA SOLICITADA: "Cuenta Corriente Origen"
                    n_cuenta = st.selectbox("Cuenta Corriente Origen", [
                        "CTA. CTE. BCI: FV ASESORIAS",
                        "CTA. CTE. BANCO CHILE: FCO",
                        "CTA. CTE. BANCO SANTANDER: NATALIA",
                        "CTA. CTE. BANCO CHILE: NATALIA"
                    ], key="n_mov_cuenta_sel")

                n_total = n_neto + n_iva
                st.info(f"💵 **Neto:** {fmt_money(n_neto)} | 🏛️ **IVA:** {fmt_money(n_iva)} {'(19% Calculado)' if n_calc_iva else '(Exento)'} | 💰 **Total Movimiento:** {fmt_money(n_total)}")

                if st.button("💾 Guardar Movimiento en BD", key="btn_save_manual_mov_btn", type="primary"):
                    n_periodo = n_fecha.strftime("%Y-%m")
                    new_db_mov = CompanyFinancialMovement(
                        empresa=empresa_sel,
                        tipo_movimiento=n_tipo,
                        categoria=n_categoria,
                        fecha=n_fecha,
                        periodo=n_periodo,
                        folio_factura=n_folio,
                        rut_contraparte=n_rut,
                        razon_social=n_razon,
                        concepto=n_concepto,
                        monto_neto=n_neto,
                        monto_iva=n_iva,
                        monto_total=n_total,
                        cuenta_corriente=n_cuenta,
                        observaciones="Registrado manualmente desde Dashboard Web"
                    )
                    db.add(new_db_mov)
                    db.commit()
                    try:
                        from src.utils.gcs_sync import upload_db_to_gcs
                        upload_db_to_gcs()
                    except Exception:
                        pass
                    st.success(f"✅ Movimiento registrado exitosamente: {n_concepto} por {fmt_money(n_total)} en {n_cuenta}.")
                    st.rerun()

        # 3. KPI METRICAS CONSOLIDADAS CON PRÉSTAMOS A SOCIOS Y SALDO BCI
        df_ingresos = df_all[df_all["Tipo"] == "INGRESO"] if not df_all.empty else pd.DataFrame()
        df_egresos = df_all[df_all["Tipo"] == "EGRESO"] if not df_all.empty else pd.DataFrame()
        df_prestamos_otorgados = df_all[df_all["Tipo"] == "PRESTAMO_SOCIO"] if not df_all.empty else pd.DataFrame()
        df_devoluciones_socio = df_all[df_all["Tipo"] == "DEVOLUCION_SOCIO"] if not df_all.empty else pd.DataFrame()

        total_ingresos = df_ingresos["Monto Total"].sum() if not df_ingresos.empty else 0.0
        total_egresos = df_egresos["Monto Total"].sum() if not df_egresos.empty else 0.0
        utilidad_neta = total_ingresos - total_egresos

        total_pres_otorgados = df_prestamos_otorgados["Monto Total"].sum() if not df_prestamos_otorgados.empty else 0.0
        total_devoluciones = df_devoluciones_socio["Monto Total"].sum() if not df_devoluciones_socio.empty else 0.0
        prestamo_neto_socio = total_pres_otorgados - total_devoluciones

        # Desglose de préstamos individuales por socio
        df_fco_p = df_prestamos_otorgados[df_prestamos_otorgados["Razón Social / Proveedor"].str.contains("FRANCISCO", na=False) | df_prestamos_otorgados["Cuenta Corriente"].str.contains("FCO", na=False)] if not df_prestamos_otorgados.empty else pd.DataFrame()
        df_fco_d = df_devoluciones_socio[df_devoluciones_socio["Razón Social / Proveedor"].str.contains("FRANCISCO", na=False) | df_devoluciones_socio["Cuenta Corriente"].str.contains("FCO", na=False)] if not df_devoluciones_socio.empty else pd.DataFrame()
        fco_neto = (df_fco_p["Monto Total"].sum() if not df_fco_p.empty else 0.0) - (df_fco_d["Monto Total"].sum() if not df_fco_d.empty else 0.0)

        df_nat_p = df_prestamos_otorgados[df_prestamos_otorgados["Razón Social / Proveedor"].str.contains("NATALIA", na=False) | df_prestamos_otorgados["Cuenta Corriente"].str.contains("NATALIA", na=False)] if not df_prestamos_otorgados.empty else pd.DataFrame()
        df_nat_d = df_devoluciones_socio[df_devoluciones_socio["Razón Social / Proveedor"].str.contains("NATALIA", na=False) | df_devoluciones_socio["Cuenta Corriente"].str.contains("NATALIA", na=False)] if not df_devoluciones_socio.empty else pd.DataFrame()
        nat_neto = (df_nat_p["Monto Total"].sum() if not df_nat_p.empty else 0.0) - (df_nat_d["Monto Total"].sum() if not df_nat_d.empty else 0.0)

        # Saldo Banco BCI disponible real (Conciliado con cartola desde BD)
        saldo_bci_base = 21160054.0
        bci_acc_db = None
        try:
            bci_acc_db = db.query(CompanyAccount).filter(
                CompanyAccount.alias == "CTA. CTE. BCI: FV ASESORIAS"
            ).first()

            if not bci_acc_db:
                bci_acc_db = CompanyAccount(
                    empresa=empresa_sel,
                    banco="Banco BCI",
                    titular=empresa_sel,
                    alias="CTA. CTE. BCI: FV ASESORIAS",
                    saldo_actual=21160054.0
                )
                db.add(bci_acc_db)
                db.commit()

            saldo_bci_base = float(bci_acc_db.saldo_actual or 21160054.0)
        except Exception:
            db.rollback()
            try:
                Base.metadata.create_all(bind=engine)
            except Exception:
                pass

        saldo_bci_real = saldo_bci_base

        st.markdown("### 📊 Indicadores Financieros Consolidados y Conciliación Bancaria")
        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.metric("🟢 Ingresos Ventas", fmt_money(total_ingresos))
        with k2:
            st.metric("🔴 Egresos Gastos", fmt_money(total_egresos))
        with k3:
            st.metric("💰 Utilidad Operacional", fmt_money(utilidad_neta))
        with k4:
            st.metric(
                "🤝 Préstamos a Socios (Consolidado)",
                fmt_money(prestamo_neto_socio),
                help=f"Préstamos consolidados desembolsados a socios de la empresa:\n• Francisco Valencia: {fmt_money(fco_neto)}\n• Natalia Tapia: {fmt_money(nat_neto)}\n• Total Consolidado: {fmt_money(prestamo_neto_socio)}"
            )
        with k5:
            st.metric(
                "🏦 Saldo Cta Cte BCI Real",
                fmt_money(saldo_bci_real),
                help="Saldo disponible real verificado en la Cta Cte Banco BCI N° 71869111 al día de hoy."
            )

        with st.expander("🏦 Módulo de Conciliación Bancaria BCI (Saldo Banco vs. Cuadratura de Caja)"):
            c_conc1, c_conc2, c_conc3 = st.columns(3)
            
            with c_conc1:
                st.markdown("##### 1. Saldo Real en Banco BCI")
                nuevo_saldo_bci = st.number_input(
                    "Saldo Disponible en Banco ($):",
                    value=float(saldo_bci_real),
                    step=100000.0,
                    format="%.0f",
                    key="input_saldo_bci_real_banco"
                )
                if st.button("💾 Actualizar Saldo Real Banco", key="btn_save_saldo_bci", type="primary", use_container_width=True):
                    if bci_acc_db:
                        bci_acc_db.saldo_actual = float(nuevo_saldo_bci)
                        db.commit()
                        try:
                            from src.utils.gcs_sync import upload_db_to_gcs
                            upload_db_to_gcs()
                        except Exception:
                            pass
                    st.success(f"✅ Saldo Banco BCI actualizado a {fmt_money(nuevo_saldo_bci)}")
                    st.rerun()

            with c_conc2:
                st.markdown("##### 2. Cuadratura Teórica de Caja")
                st.markdown(f"""
                <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155;'>
                    <p style='margin: 0; color: #e2e8f0;'>
                        💰 <b>Utilidad Acumulada Operaciones:</b> <span style='color: #10b981;'>{fmt_money(utilidad_neta)}</span><br/>
                        🤝 <b>Préstamos a Socios de Caja:</b> <span style='color: #ef4444;'>-{fmt_money(prestamo_neto_socio)}</span><br/>
                        <hr style='border-color: #475569; margin: 8px 0;'/>
                        📊 <b>Caja Líquida Teórica:</b> <span style='font-weight: bold; color: #38bdf8;'>{fmt_money(utilidad_neta - prestamo_neto_socio)}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with c_conc3:
                descalce_caja = saldo_bci_real - (utilidad_neta - prestamo_neto_socio)
                st.markdown("##### 3. Conciliación de Saldos")
                st.markdown(f"""
                <div style='background-color: #0f172a; padding: 15px; border-radius: 10px; border-left: 5px solid {"#10b981" if abs(descalce_caja) < 1000000 else "#f59e0b"};'>
                    <h4 style='margin: 0; color: #f8fafc;'>🏦 Saldo Banco Real: {fmt_money(saldo_bci_real)}</h4>
                    <p style='color: #94a3b8; font-size: 0.9em; margin-top: 5px; margin-bottom: 0;'>
                        📊 Caja Teórica (Utilidad - Préstamos): {fmt_money(utilidad_neta - prestamo_neto_socio)}<br/>
                        ⚖️ Ajuste Impuestos / F29 / Giros: <b>{fmt_money(descalce_caja)}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # 4. GRAFICOS Y DISTRIBUCION
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            st.markdown("##### 📈 Ingresos vs Egresos por Mes")
            df_mov_graf = df_all[df_all["Tipo"].isin(["INGRESO", "EGRESO"])]
            if not df_mov_graf.empty and "Período" in df_mov_graf.columns:
                df_grouped = df_mov_graf.groupby(["Período", "Tipo"])["Monto Total"].sum().reset_index()
                if not df_grouped.empty:
                    fig_bar = px.bar(
                        df_grouped,
                        x="Período",
                        y="Monto Total",
                        color="Tipo",
                        barmode="group",
                        color_discrete_map={"INGRESO": "#10b981", "EGRESO": "#ef4444"},
                        title="Evolución Mensual de Operaciones"
                    )
                    fig_bar.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Sin datos suficientes para graficar mensualidad.")
            else:
                st.info("Sin registros de movimientos.")

        with gcol2:
            st.markdown("##### 🍕 Desglose de Gastos por Categoría")
            if not df_egresos.empty:
                df_cat = df_egresos.groupby("Categoría")["Monto Total"].sum().reset_index()
                fig_pie = px.pie(
                    df_cat,
                    values="Monto Total",
                    names="Categoría",
                    title="Distribución de Egresos",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_pie.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Sin registros de egresos para clasificar.")

        st.markdown("---")

        # 5. TABLAS EDITABLES CON ST.DATA_EDITOR
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🟢 Facturas Emitidas / Abonos",
            "🔴 Facturas de Compra / Gastos",
            "🤝 Movimientos Cuentas Socios (Francisco & Natalia)",
            "🏛️ Estimación Impuestos F29",
            "🏦 Desglose por Cuentas Corrientes"
        ])

        with tab1:
            st.markdown("##### 🟢 Registro de Facturación Emitida e Ingresos")
            st.caption("Edita directamente los valores o agrégale observaciones. Presiona 'Guardar Cambios' para sincronizar con la BD.")

            df_ing_view = df_ingresos.copy()
            if not df_ing_view.empty:
                cols_show = ["ID", "Fecha", "Período", "Folio", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"]
                df_ing_view = df_ing_view[cols_show]

            cs1, cs2 = st.columns([2.5, 1.5])
            with cs1:
                sort_ing = st.selectbox("🔃 Ordenar Ingresos por:", [
                    "Fecha (Más reciente primero)",
                    "Fecha (Más antigua primero)",
                    "Monto Total (Mayor a Menor)",
                    "Monto Total (Menor a Mayor)",
                    "Concepto / Detalle (A-Z)",
                    "Concepto / Detalle (Z-A)",
                    "N° Factura / Folio (Mayor a Menor)",
                    "N° Factura / Folio (Menor a Mayor)"
                ], key="sort_ing_sel")

            if not df_ing_view.empty:
                if "Fecha (Más reciente" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Fecha", ascending=False)
                elif "Fecha (Más antigua" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Fecha", ascending=True)
                elif "Monto Total (Mayor a Menor)" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Monto Total", ascending=False)
                elif "Monto Total (Menor a Mayor)" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Monto Total", ascending=True)
                elif "Concepto / Detalle (A-Z)" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Concepto / Detalle", ascending=True)
                elif "Concepto / Detalle (Z-A)" in sort_ing: df_ing_view = df_ing_view.sort_values(by="Concepto / Detalle", ascending=False)
                elif "Folio (Mayor a Menor)" in sort_ing:
                    df_ing_view["_folio_num"] = pd.to_numeric(df_ing_view["Folio"], errors="coerce").fillna(0)
                    df_ing_view = df_ing_view.sort_values(by="_folio_num", ascending=False).drop(columns=["_folio_num"])
                elif "Folio (Menor a Mayor)" in sort_ing:
                    df_ing_view["_folio_num"] = pd.to_numeric(df_ing_view["Folio"], errors="coerce").fillna(0)
                    df_ing_view = df_ing_view.sort_values(by="_folio_num", ascending=True).drop(columns=["_folio_num"])

            df_ing_view = df_ing_view.reset_index(drop=True)
            edited_ing = st.data_editor(
                df_ing_view,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                disabled=["ID"],
                key="editor_ingresos_fv",
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width=50),
                    "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", width=95),
                    "Período": st.column_config.TextColumn("Período", width=75),
                    "Folio": st.column_config.TextColumn("N° Folio", width=75),
                    "Concepto / Detalle": st.column_config.TextColumn("Concepto / Detalle", width=250),
                    "Monto Neto": st.column_config.NumberColumn("Neto ($)", format="$ %,.0f", width=120),
                    "IVA": st.column_config.NumberColumn("IVA ($)", format="$ %,.0f", width=100),
                    "Monto Total": st.column_config.NumberColumn("Total ($)", format="$ %,.0f", width=120),
                    "Cuenta Corriente": st.column_config.TextColumn("Cuenta Corriente", width=180),
                    "Observaciones": st.column_config.TextColumn("Observaciones", width=200)
                }
            )

            if st.button("💾 Guardar Cambios en Ingresos", key="btn_save_ing", type="primary"):
                orig_ids_ing = set()
                if not df_ing_view.empty and "ID" in df_ing_view.columns:
                    orig_ids_ing = set(df_ing_view["ID"].dropna().astype(int))

                current_ids_ing = set()
                for idx, row in edited_ing.iterrows():
                    m_id = row.get("ID")
                    if pd.notna(m_id) and str(m_id).strip() != "" and str(m_id).strip() != "nan":
                        m_int = int(m_id)
                        current_ids_ing.add(m_int)
                        mov_db = db.query(CompanyFinancialMovement).filter_by(id=m_int).first()
                        if mov_db:
                            f_val = row.get("Fecha")
                            if f_val:
                                try:
                                    if isinstance(f_val, str): f_dt = datetime.strptime(f_val, "%Y-%m-%d").date()
                                    elif hasattr(f_val, "date"): f_dt = f_val.date()
                                    else: f_dt = f_val
                                    mov_db.fecha = f_dt
                                    mov_db.periodo = f_dt.strftime("%Y-%m")
                                except: pass
                            mov_db.concepto = str(row.get("Concepto / Detalle", ""))
                            mov_db.folio_factura = str(row.get("Folio", ""))
                            mov_db.monto_neto = float(row.get("Monto Neto", 0.0) or 0.0)
                            mov_db.monto_iva = float(row.get("IVA", 0.0) or 0.0)
                            tot_c = float(row.get("Monto Total", 0.0) or 0.0)
                            if tot_c == 0: tot_c = mov_db.monto_neto + mov_db.monto_iva
                            mov_db.monto_total = tot_c
                            mov_db.cuenta_corriente = str(row.get("Cuenta Corriente", ""))
                            mov_db.observaciones = str(row.get("Observaciones", ""))
                    else:
                        # NUEVO INGRESO AGREGADO DINÁMICAMENTE EN TABLA
                        neto_val = float(row.get("Monto Neto", 0.0) or 0.0)
                        iva_val = float(row.get("IVA", 0.0) or 0.0)
                        tot_val = float(row.get("Monto Total", 0.0) or 0.0)
                        if tot_val == 0.0: tot_val = neto_val + iva_val

                        if tot_val > 0 or row.get("Concepto / Detalle"):
                            f_val = row.get("Fecha")
                            try:
                                if isinstance(f_val, str): f_dt = datetime.strptime(f_val, "%Y-%m-%d").date()
                                elif hasattr(f_val, "date"): f_dt = f_val.date()
                                else: f_dt = datetime.today().date()
                            except:
                                f_dt = datetime.today().date()

                            new_mov = CompanyFinancialMovement(
                                empresa=empresa_sel,
                                tipo_movimiento="INGRESO",
                                categoria="FACTURACION / ABONO",
                                fecha=f_dt,
                                periodo=f_dt.strftime("%Y-%m"),
                                folio_factura=str(row.get("Folio", "")),
                                concepto=str(row.get("Concepto / Detalle", "")),
                                monto_neto=neto_val,
                                monto_iva=iva_val,
                                monto_total=tot_val,
                                cuenta_corriente=str(row.get("Cuenta Corriente", "CTA. CTE. BCI: FV ASESORIAS")),
                                observaciones=str(row.get("Observaciones", "Agregado en tabla editable"))
                            )
                            db.add(new_mov)

                # Eliminar de BD filas borradas en la tabla por el usuario
                for d_id in (orig_ids_ing - current_ids_ing):
                    del_mov = db.query(CompanyFinancialMovement).filter_by(id=d_id).first()
                    if del_mov: db.delete(del_mov)

                db.commit()
                st.success("✅ Cambios en Ingresos guardados en la Base de Datos.")
                st.rerun()

            with st.expander("🗑️ Eliminar un Ingreso Específico de la BD"):
                db_ing_movs = db.query(CompanyFinancialMovement).filter_by(empresa=empresa_sel, tipo_movimiento="INGRESO").order_by(CompanyFinancialMovement.id.desc()).all()
                if db_ing_movs:
                    opts_del_ing = {f"ID {m.id} | {m.fecha} | {m.razon_social or 'S/P'} | {m.concepto or ''} | Total: {fmt_money(m.monto_total)}": m.id for m in db_ing_movs}
                    sel_del_ing_str = st.selectbox("Seleccione el ingreso a eliminar:", list(opts_del_ing.keys()), key="sel_del_ing_opt")
                    if st.button("🗑️ Confirmar y Eliminar Ingreso", key="btn_confirm_del_ing", type="primary"):
                        target_id = opts_del_ing[sel_del_ing_str]
                        mov_to_del = db.query(CompanyFinancialMovement).filter_by(id=target_id).first()
                        if mov_to_del:
                            db.delete(mov_to_del)
                            db.commit()
                            st.success(f"✅ Ingreso ID {target_id} eliminado exitosamente.")
                            st.rerun()
                else:
                    st.info("No hay ingresos registrados para eliminar.")

        with tab2:
            st.markdown("##### 🔴 Registro de Facturas de Compra, Gastos y Arriendos")
            st.caption("Puedes agregar nuevas filas al final de la tabla (ej: Arriendo), editar campos directamente o borrar filas. Presiona 'Guardar Cambios en Egresos' para persistir.")

            df_egr_view = df_egresos.copy()
            if not df_egr_view.empty:
                cols_show = ["ID", "Fecha", "Período", "Categoría", "RUT", "Razón Social / Proveedor", "Concepto / Detalle", "Monto Neto", "IVA", "Monto Total", "Cuenta Corriente", "Observaciones"]
                df_egr_view = df_egr_view[cols_show]

            cse1, cse2 = st.columns([2.5, 1.5])
            with cse1:
                sort_egr = st.selectbox("🔃 Ordenar Egresos por:", [
                    "Fecha (Más reciente primero)",
                    "Fecha (Más antigua primero)",
                    "Monto Total (Mayor a Menor)",
                    "Monto Total (Menor a Mayor)",
                    "Proveedor (A-Z)",
                    "Proveedor (Z-A)",
                    "Categoría (A-Z)"
                ], key="sort_egr_sel")

            if not df_egr_view.empty:
                if "Fecha (Más reciente" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Fecha", ascending=False)
                elif "Fecha (Más antigua" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Fecha", ascending=True)
                elif "Monto Total (Mayor a Menor)" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Monto Total", ascending=False)
                elif "Monto Total (Menor a Mayor)" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Monto Total", ascending=True)
                elif "Proveedor (A-Z)" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Razón Social / Proveedor", ascending=True)
                elif "Proveedor (Z-A)" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Razón Social / Proveedor", ascending=False)
                elif "Categoría" in sort_egr: df_egr_view = df_egr_view.sort_values(by="Categoría", ascending=True)

            df_egr_view = df_egr_view.reset_index(drop=True)
            edited_egr = st.data_editor(
                df_egr_view,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                disabled=["ID"],
                key="editor_egresos_fv",
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width=50),
                    "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", width=95),
                    "Período": st.column_config.TextColumn("Período", width=75),
                    "Categoría": st.column_config.SelectboxColumn("Categoría", options=["ARRIENDO", "GASTO / COMPRA", "PAGO SUELDOS SOCIO", "IMPUESTOS F29", "REEMBOLSO GASTO / COMPRA SOCIO", "SERVICIOS", "OTROS"], width=130),
                    "RUT": st.column_config.TextColumn("RUT", width=95),
                    "Razón Social / Proveedor": st.column_config.TextColumn("Proveedor / Entidad", width=180),
                    "Concepto / Detalle": st.column_config.TextColumn("Concepto / Detalle", width=220),
                    "Monto Neto": st.column_config.NumberColumn("Neto ($)", format="$ %,.0f", width=120),
                    "IVA": st.column_config.NumberColumn("IVA ($)", format="$ %,.0f", width=100),
                    "Monto Total": st.column_config.NumberColumn("Total ($)", format="$ %,.0f", width=120),
                    "Cuenta Corriente": st.column_config.SelectboxColumn("Cuenta Corriente", options=[
                        "CTA. CTE. BCI: FV ASESORIAS",
                        "CTA. CTE. BANCO CHILE: FCO",
                        "CTA. CTE. BANCO SANTANDER: NATALIA",
                        "CTA. CTE. BANCO CHILE: NATALIA"
                    ], width=180),
                    "Observaciones": st.column_config.TextColumn("Observaciones", width=200)
                }
            )

            if st.button("💾 Guardar Cambios en Egresos (Incluye Arriendos/Gastos Nuevos)", key="btn_save_egr", type="primary"):
                orig_ids_egr = set()
                if not df_egr_view.empty and "ID" in df_egr_view.columns:
                    orig_ids_egr = set(df_egr_view["ID"].dropna().astype(int))

                current_ids_egr = set()
                for idx, row in edited_egr.iterrows():
                    m_id = row.get("ID")
                    if pd.notna(m_id) and str(m_id).strip() != "" and str(m_id).strip() != "nan":
                        m_int = int(m_id)
                        current_ids_egr.add(m_int)
                        mov_db = db.query(CompanyFinancialMovement).filter_by(id=m_int).first()
                        if mov_db:
                            f_val = row.get("Fecha")
                            if pd.notna(f_val):
                                try:
                                    if isinstance(f_val, str): f_dt = datetime.strptime(f_val, "%Y-%m-%d").date()
                                    elif hasattr(f_val, "date"): f_dt = f_val.date()
                                    else: f_dt = f_val
                                    
                                    if pd.isna(f_dt): 
                                        f_dt = datetime.today().date()
                                        
                                    mov_db.fecha = f_dt
                                    mov_db.periodo = f_dt.strftime("%Y-%m")
                                except: pass
                            mov_db.razon_social = str(row.get("Razón Social / Proveedor", ""))
                            mov_db.concepto = str(row.get("Concepto / Detalle", ""))
                            mov_db.categoria = str(row.get("Categoría", "ARRIENDO"))
                            mov_db.rut_contraparte = str(row.get("RUT", ""))
                            mov_db.monto_neto = float(row.get("Monto Neto", 0.0) or 0.0)
                            mov_db.monto_iva = float(row.get("IVA", 0.0) or 0.0)
                            tot_c = float(row.get("Monto Total", 0.0) or 0.0)
                            if tot_c == 0: tot_c = mov_db.monto_neto + mov_db.monto_iva
                            mov_db.monto_total = tot_c
                            mov_db.cuenta_corriente = str(row.get("Cuenta Corriente", ""))
                            mov_db.observaciones = str(row.get("Observaciones", ""))
                    else:
                        # NUEVO EGRESO / ARRIENDO AGREGADO DINÁMICAMENTE
                        neto_val = float(row.get("Monto Neto", 0.0) or 0.0)
                        iva_val = float(row.get("IVA", 0.0) or 0.0)
                        tot_val = float(row.get("Monto Total", 0.0) or 0.0)
                        if tot_val == 0.0: tot_val = neto_val + iva_val

                        if tot_val > 0 or row.get("Concepto / Detalle") or row.get("Razón Social / Proveedor"):
                            f_val = row.get("Fecha")
                            f_dt = datetime.today().date()
                            if pd.notna(f_val):
                                try:
                                    if isinstance(f_val, str): f_dt = datetime.strptime(f_val, "%Y-%m-%d").date()
                                    elif hasattr(f_val, "date"): f_dt = f_val.date()
                                    else: f_dt = f_val
                                except:
                                    pass
                            
                            if pd.isna(f_dt):
                                f_dt = datetime.today().date()

                            cat_val = str(row.get("Categoría", "ARRIENDO")).strip() or "ARRIENDO"
                            new_mov = CompanyFinancialMovement(
                                empresa=empresa_sel,
                                tipo_movimiento="EGRESO",
                                categoria=cat_val,
                                fecha=f_dt,
                                periodo=f_dt.strftime("%Y-%m"),
                                rut_contraparte=str(row.get("RUT", "")),
                                razon_social=str(row.get("Razón Social / Proveedor", "Inmobiliaria / Arriendo")),
                                concepto=str(row.get("Concepto / Detalle", "Pago de Arriendo Oficina")),
                                monto_neto=neto_val,
                                monto_iva=iva_val,
                                monto_total=tot_val,
                                cuenta_corriente=str(row.get("Cuenta Corriente", "CTA. CTE. BCI: FV ASESORIAS")),
                                observaciones=str(row.get("Observaciones", "Registrado en tabla editable"))
                            )
                            db.add(new_mov)

                # Eliminar de BD filas borradas en la tabla por el usuario
                for d_id in (orig_ids_egr - current_ids_egr):
                    del_mov = db.query(CompanyFinancialMovement).filter_by(id=d_id).first()
                    if del_mov: db.delete(del_mov)

                db.commit()
                st.success("✅ Egresos y nuevos pagos (Arriendo/Gastos) guardados exitosamente.")
                st.rerun()

            with st.expander("🗑️ Eliminar un Egreso / Arriendo Específico de la BD"):
                db_egr_movs = db.query(CompanyFinancialMovement).filter_by(empresa=empresa_sel, tipo_movimiento="EGRESO").order_by(CompanyFinancialMovement.id.desc()).all()
                if db_egr_movs:
                    opts_del_egr = {f"ID {m.id} | {m.fecha} | {m.razon_social or 'S/P'} | {m.concepto or ''} | Total: {fmt_money(m.monto_total)}": m.id for m in db_egr_movs}
                    sel_del_egr_str = st.selectbox("Seleccione el egreso a eliminar:", list(opts_del_egr.keys()), key="sel_del_egr_opt")
                    if st.button("🗑️ Confirmar y Eliminar Egreso", key="btn_confirm_del_egr", type="primary"):
                        target_id = opts_del_egr[sel_del_egr_str]
                        mov_to_del = db.query(CompanyFinancialMovement).filter_by(id=target_id).first()
                        if mov_to_del:
                            db.delete(mov_to_del)
                            db.commit()
                            st.success(f"✅ Egreso ID {target_id} eliminado exitosamente.")
                            st.rerun()
                else:
                    st.info("No hay egresos registrados para eliminar.")

        with tab3:
            st.markdown("##### 🤝 Registro de Cuentas Corrientes y Movimientos de Socios")
            st.caption("Detalle de préstamos, pago de sueldos y reembolsos de gastos personales efectuados para la empresa.")

            df_socio_all = df_all[df_all["Tipo"].isin(["PRESTAMO_SOCIO", "DEVOLUCION_SOCIO", "MOVIMIENTO_CTA_CTE"])].copy()

            cs_filt, cs_blank = st.columns([2.5, 1.5])
            with cs_filt:
                socio_sel = st.radio("👤 Filtrar por Socio:", ["👥 Todos los Socios", "👨🏻‍💼 Francisco Valencia", "👩🏻‍💼 Natalia Tapia"], horizontal=True)

            df_socio_view = df_socio_all.copy()
            if socio_sel == "👨🏻‍💼 Francisco Valencia":
                df_socio_view = df_socio_view[df_socio_view["Razón Social / Proveedor"].str.contains("FRANCISCO", na=False) | df_socio_view["Cuenta Corriente"].str.contains("FCO", na=False)]
            elif socio_sel == "👩🏻‍💼 Natalia Tapia":
                df_socio_view = df_socio_view[df_socio_view["Razón Social / Proveedor"].str.contains("NATALIA", na=False) | df_socio_view["Cuenta Corriente"].str.contains("NATALIA", na=False)]

            if not df_socio_view.empty:
                cols_show_socio = ["ID", "Fecha", "Razón Social / Proveedor", "Categoría", "Concepto / Detalle", "Cuenta Corriente", "Monto Total", "Observaciones"]
                df_socio_view = df_socio_view[cols_show_socio]

                st.dataframe(
                    df_socio_view,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", width="small"),
                        "Razón Social / Proveedor": st.column_config.TextColumn("Socio / Beneficiario", width="medium"),
                        "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
                        "Concepto / Detalle": st.column_config.TextColumn("Concepto / Detalle", width="large"),
                        "Cuenta Corriente": st.column_config.TextColumn("Cuenta Destino/Origen", width="medium"),
                        "Monto Total": st.column_config.NumberColumn("Monto ($)", format="$ %,.0f", width="medium"),
                        "Observaciones": st.column_config.TextColumn("Observaciones", width="medium")
                    }
                )

                # Calcular resúmenes individuales
                df_fco = df_socio_all[df_socio_all["Razón Social / Proveedor"].str.contains("FRANCISCO", na=False) | df_socio_all["Cuenta Corriente"].str.contains("FCO", na=False)]
                df_nat = df_socio_all[df_socio_all["Razón Social / Proveedor"].str.contains("NATALIA", na=False) | df_socio_all["Cuenta Corriente"].str.contains("NATALIA", na=False)]

                fco_pres = df_fco[df_fco["Tipo"] == "PRESTAMO_SOCIO"]["Monto Total"].sum() - df_fco[df_fco["Tipo"] == "DEVOLUCION_SOCIO"]["Monto Total"].sum()
                fco_reembolsos = df_fco[df_fco["Tipo"] == "MOVIMIENTO_CTA_CTE"]["Monto Total"].sum()

                nat_sueldos = df_nat[df_nat["Categoría"].str.contains("SUELDO", na=False)]["Monto Total"].sum()
                nat_reembolsos = df_nat[~df_nat["Categoría"].str.contains("SUELDO", na=False)]["Monto Total"].sum()

                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown(f"""
                    <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #38bdf8;'>
                        <h4 style='color: #38bdf8; margin: 0;'>👨🏻‍💼 Resumen Socio: Francisco Valencia</h4>
                        <p style='color: #e2e8f0; font-size: 1rem; margin-top: 8px;'>
                            • <b>Préstamo Acumulado Neto:</b> <span style='color: #f43f5e; font-weight: bold;'>{fmt_money(fco_pres)}</span><br/>
                            • <b>Reembolsos de Compras Personales:</b> {fmt_money(fco_reembolsos)}<br/>
                            • <i>Cta. Cte. Origen: Banco de Chile FCO</i>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with r_col2:
                    st.markdown(f"""
                    <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #ec4899;'>
                        <h4 style='color: #ec4899; margin: 0;'>👩🏻‍💼 Resumen Socia: Natalia Tapia</h4>
                        <p style='color: #e2e8f0; font-size: 1rem; margin-top: 8px;'>
                            • <b>Pago Sueldos Acumulados:</b> {fmt_money(nat_sueldos)}<br/>
                            • <b>Reembolsos de Compras (Easy, Aseo, etc.):</b> {fmt_money(nat_reembolsos)}<br/>
                            • <i>Cta. Cte. Origen: Banco Santander Natalia</i>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.info("Sin registros de préstamos o movimientos de cuenta corriente socio.")

        with tab4:
            st.markdown("##### 🏛️ Detalle Impuestos F29 por Período (Consolidado Unificado)")
            st.info("Cálculo estimado de IVA Débito Fiscal (19% ventas) menos IVA Crédito Fiscal (19% compras).")

            if not df_all.empty and "Período" in df_all.columns:
                df_valid = df_all[df_all["Período"].str.contains(r"^\d{4}-\d{2}$", na=False)]
                if not df_valid.empty:
                    df_f29 = df_valid.groupby(["Período", "Tipo"])["IVA"].sum().unstack(fill_value=0).reset_index()
                    if "INGRESO" not in df_f29.columns: df_f29["INGRESO"] = 0.0
                    if "EGRESO" not in df_f29.columns: df_f29["EGRESO"] = 0.0
                    
                    df_f29["IVA Débito (Ventas)"] = df_f29["INGRESO"]
                    df_f29["IVA Crédito (Compras)"] = df_f29["EGRESO"]
                    df_f29["Impuesto IVA a Pagar"] = df_f29["IVA Débito (Ventas)"] - df_f29["IVA Crédito (Compras)"]

                    st.dataframe(
                        df_f29[["Período", "IVA Débito (Ventas)", "IVA Crédito (Compras)", "Impuesto IVA a Pagar"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Período": st.column_config.TextColumn("Período (Año-Mes)", width="small"),
                            "IVA Débito (Ventas)": st.column_config.NumberColumn("IVA Débito (Ventas)", format="$ %,.0f", width="medium"),
                            "IVA Crédito (Compras)": st.column_config.NumberColumn("IVA Crédito (Compras)", format="$ %,.0f", width="medium"),
                            "Impuesto IVA a Pagar": st.column_config.NumberColumn("Impuesto IVA a Pagar", format="$ %,.0f", width="medium")
                        }
                    )

        with tab5:
            st.markdown("##### 🏦 Desglose de Movimientos por Cuenta Corriente")
            if not df_all.empty:
                df_cta = df_all.groupby(["Cuenta Corriente", "Tipo"])["Monto Total"].sum().unstack(fill_value=0).reset_index()
                if "INGRESO" not in df_cta.columns: df_cta["INGRESO"] = 0.0
                if "EGRESO" not in df_cta.columns: df_cta["EGRESO"] = 0.0
                df_cta["Balance Neto de Cuenta"] = df_cta["INGRESO"] - df_cta["EGRESO"]

                st.dataframe(
                    df_cta[["Cuenta Corriente", "INGRESO", "EGRESO", "Balance Neto de Cuenta"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Cuenta Corriente": st.column_config.TextColumn("Cuenta Corriente", width="medium"),
                        "INGRESO": st.column_config.NumberColumn("Abonos Totales", format="$ %,.0f", width="medium"),
                        "EGRESO": st.column_config.NumberColumn("Cargos/Gastos Totales", format="$ %,.0f", width="medium"),
                        "Balance Neto de Cuenta": st.column_config.NumberColumn("Flujo Neto", format="$ %,.0f", width="medium")
                    }
                )

    except Exception as e:
        import traceback
        st.error(f"Error en UI de Gestión Empresarial: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()
