import streamlit as st
import os
import sys
import importlib
import pandas as pd
import generador_informes
importlib.reload(generador_informes)
from generador_informes import generar_pdf_bytes

# Ensure we can import herencia_calculator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.herencia_calculator import HerenciaCalculator
from src.utils.pdf_generator import generate_reporte_360_from_markdown
from src.utils.docx_generator_macro import generar_docx_reporte_360
import tempfile

def auto_generate_markdown(carteras, combinadas=True, llave_especifica=None):
    md = ""
    
    # Inyectar las notas estratégicas si fueron provistas en el auditor
    notas = st.session_state.get('notas_estrategicas_auditor', '').strip()
    if notas:
        md += "## 🧠 Tesis de Reestructuración & Estrategia\n\n"
        md += f"> *{notas}*\n\n---\n\n"
        
    # Inyectar Análisis 360 si existe
    if 'reporte_360_data' in st.session_state:
        d = st.session_state['reporte_360_data']
        
        # Inyectar bloque de estilos CSS para xhtml2pdf
        md += """
<style>
    .table-360 {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        page-break-inside: avoid;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 8.5pt;
    }
    .table-360 th {
        background-color: #0A2342;
        color: #ffffff;
        padding: 8px;
        text-align: left;
        border: 1px solid #1E3A5F;
    }
    .table-360 td {
        padding: 8px;
        border: 1px solid #e2e8f0;
        vertical-align: middle;
    }
    .row-even { background-color: #f8fafc; }
    .row-odd { background-color: #ffffff; }
    .highlight-val { font-weight: bold; color: #0A2342; }
    .highlight-net { font-weight: bold; color: #047857; }
    .highlight-deficit { font-weight: bold; color: #b91c1c; }
</style>
"""
        md += "## 🌐 Análisis Patrimonial 360°\n\n"
        
        # Propiedades Inmobiliarias
        md += "### 🏢 Cartera Inmobiliaria Enriquecida\n\n"
        if d.get("propiedades"):
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Propiedad</th><th>Uso</th><th>Valor Comercial</th><th>Arriendo</th><th>GGCC & Seguros</th><th>Contribuciones (Trim.)</th><th>Flujo Neto Mensual</th><th>Cap Rate</th></tr></thead>\n'
            md += '<tbody>\n'
            for idx, p in enumerate(d["propiedades"]):
                row_class = "row-even" if idx % 2 == 0 else "row-odd"
                md += f'<tr class="{row_class}">'
                md += f'<td>{p["nombre"]}</td>'
                md += f'<td>{p["destino"]}</td>'
                md += f'<td class="highlight-val">{p["valor_uf"]:,.0f} UF</td>'
                md += f'<td>${p["arriendo"]:,.0f}</td>'
                ggcc_seg = p["gastos_comunes"] + p["seguros"]
                md += f'<td>${ggcc_seg:,.0f}</td>'
                md += f'<td>${p["contribuciones"]:,.0f}</td>'
                md += f'<td class="highlight-net">${p["flujo_neto"]:,.0f}</td>'
                md += f'<td>{p["cap_rate"]:.2f}%</td>'
                md += '</tr>\n'
            md += '</tbody></table>\n\n'
        else:
            md += "> *Sin activos inmobiliarios registrados.*\n\n"
            
        # Inversiones
        md += "### 📈 Matriz de Inversiones\n\n"
        if d.get("inversiones"):
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Institución / Portafolio</th><th>Clase de Activo</th><th>Nivel de Riesgo</th><th>Moneda</th><th>Monto Actual</th><th>TIR Proyectada</th><th>Rentabilidad Acum.</th></tr></thead>\n'
            md += '<tbody>\n'
            for idx, inv in enumerate(d["inversiones"]):
                row_class = "row-even" if idx % 2 == 0 else "row-odd"
                md += f'<tr class="{row_class}">'
                md += f'<td>{inv["nombre"]}</td>'
                md += f'<td>{inv["tipo"]}</td>'
                md += f'<td>{inv["riesgo"]}</td>'
                md += f'<td>{inv["moneda"]}</td>'
                md += f'<td class="highlight-val">${inv["monto"]:,.0f}</td>'
                md += f'<td>{inv["tir"]:.2f}%</td>'
                md += f'<td>{inv["rentabilidad"]:.2f}%</td>'
                md += '</tr>\n'
            md += '</tbody></table>\n\n'
        else:
            md += "> *Sin inversiones estructuradas registradas.*\n\n"
            
        # Flujo Sucesorio
        md += "### 💼 Presupuesto y Flujo de Caja Sucesorio (Post-Mortem)\n\n"
        if d.get("flujo_sucesorio"):
            fs = d["flujo_sucesorio"]
            
            # Tabla de detalle de gastos
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Concepto de Gasto Operativo</th><th>Monto Mensual</th><th>Proyección Anual</th></tr></thead>\n'
            md += '<tbody>\n'
            
            md += f'<tr class="row-even"><td>Gastos de Vida y Familia</td><td>${fs["gastos_vida"]:,.0f}</td><td>${fs["gastos_vida"]*12:,.0f}</td></tr>\n'
            md += f'<tr class="row-odd"><td>Sueldos y Servicios Domésticos</td><td>${fs["sueldos"]:,.0f}</td><td>${fs["sueldos"]*12:,.0f}</td></tr>\n'
            md += f'<tr class="row-even"><td>Compromisos Fijos de Activos</td><td>${fs["compromisos"]:,.0f}</td><td>${fs["compromisos"]*12:,.0f}</td></tr>\n'
            md += f'<tr class="row-odd"><td>Seguros Generales y de Vida</td><td>${fs["seguros"]:,.0f}</td><td>${fs["seguros"]*12:,.0f}</td></tr>\n'
            
            try:
                calc = HerenciaCalculator()
                res_flujo = calc.calcular_flujo_caja_sucesorio(
                    ingresos_pasivos_mensuales=fs['ingresos_pasivos'],
                    gastos_vida=fs['gastos_vida'],
                    sueldos_servicios=fs['sueldos'],
                    compromisos_fijos=fs['compromisos'],
                    seguros_vigentes=fs['seguros']
                )
                
                md += f'<tr class="row-even" style="background-color: #e2e8f0;"><td><b>Total Gastos Estimados</b></td><td class="highlight-val">${res_flujo["gastos_mensuales_totales"]:,.0f}</td><td class="highlight-val">${res_flujo["gastos_anuales_totales"]:,.0f}</td></tr>\n'
                md += f'<tr class="row-odd"><td>Ingresos Pasivos Proyectados</td><td class="highlight-net">${fs["ingresos_pasivos"]:,.0f}</td><td class="highlight-net">${fs["ingresos_pasivos"]*12:,.0f}</td></tr>\n'
                
                estado_class = "highlight-deficit" if res_flujo['estado_flujo'] == "DÉFICIT" else "highlight-net"
                md += f'<tr class="row-even"><td><b>FLUJO NETO</b></td><td class="{estado_class}">${res_flujo["flujo_neto_mensual"]:,.0f}</td><td class="{estado_class}">${res_flujo["flujo_neto_anual"]:,.0f}</td></tr>\n'
                md += '</tbody></table>\n\n'
                
                if res_flujo['estado_flujo'] == "DÉFICIT":
                    md += f"#### ⚠️ Brecha Patrimonial Sucesoria: <span style='color: #b91c1c;'>${res_flujo['brecha_sucesoria_capital_requerido']:,.0f}</span>\n"
                    md += f"<p style='font-size: 8pt; color: #4b5563;'>* Capital líquido adicional sugerido para cubrir el déficit perpetuo, asumiendo una rentabilidad / tasa libre de riesgo del {res_flujo['tasa_retiro_asumida']*100:.1f}% anual (Holgura Financiera).</p>\n\n"
                else:
                    md += "#### ✅ Cobertura Suficiente\n<p style='font-size: 8pt; color: #4b5563;'>Los ingresos pasivos estructurados logran cubrir satisfactoriamente los compromisos mensuales del estándar de vida proyectado.</p>\n\n"
            except Exception as e:
                md += '</tbody></table>\n\n'
        else:
            md += "> *No se han configurado parámetros de flujo de caja sucesorio.*\n\n"
            
        md += "---\n\n"
        
        # Optimización Tributaria
        md += "### 📉 Optimización Tributaria y Fuga Fiscal\n\n"
        hipo = d.get('intereses_hipotecarios', 0)
        edu = d.get('gastos_educacion', 0)
        
        if hipo > 0 or edu > 0:
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Beneficio Tributario Detectado</th><th>Monto Anual (CLP)</th><th>Impacto en Liquidez</th></tr></thead>\n'
            md += '<tbody>\n'
            
            if hipo > 0:
                md += f'<tr class="row-even"><td>Rebaja Intereses Hipotecarios (Art. 55 bis)</td><td>${hipo:,.0f}</td><td>Deducción Directa de la Base Imponible</td></tr>\n'
            
            if edu > 0:
                # La clase row-odd u row-even se intercala, pero para simplificar usamos row-odd
                md += f'<tr class="row-odd"><td>Crédito por Gastos en Educación (Art. 55 ter)</td><td>${edu:,.0f}</td><td>Crédito Directo contra IGC</td></tr>\n'
                
            md += '</tbody></table>\n\n'
            md += "<div class='tax-callout'><b>⚠️ Nota Tributaria:</b> La devolución fiscal recuperable final dependerá del Tramo Marginal de Impuesto Global Complementario (IGC) del contribuyente (simulable en Altus AI).</div>\n\n"
        else:
            md += "> *No se han registrado beneficios tributarios (Art. 55 bis/ter) estructurados para este cliente.*\n\n"
            
        md += "---\n\n"

        # Auditoría de Pólizas
        md += "### 🛡️ Auditoría Patrimonial de Seguros\n\n"
        if d.get("audit_seguros") and d["audit_seguros"].get("polizas"):
            ad = d["audit_seguros"]
            
            # Tabla Clasificada de Pólizas
            md += "#### Desglose y Clasificación de Pólizas\n"
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Compañía</th><th>Contratante</th><th>Tipo de Cobertura</th><th>Destino del Beneficio</th></tr></thead>\n'
            md += '<tbody>\n'
            for i, p in enumerate(ad["polizas"]):
                row_class = "row-even" if i % 2 == 0 else "row-odd"
                compania = p.get('compania', 'N/A')
                contratante = p.get('contratante', 'N/A')
                tipo = p.get('tipo', 'N/A')
                destino = p.get('destino_beneficio', 'N/A')
                md += f'<tr class="{row_class}"><td>{compania}</td><td>{contratante}</td><td>{tipo}</td><td>{destino}</td></tr>\n'
            md += '</tbody></table>\n\n'
            
            md += "#### Resumen Financiero y Brecha Sucesoria\n"
            md += '<table class="table-360">\n'
            md += '<thead><tr><th>Métrica Sucesoria</th><th>Monto (UF)</th></tr></thead>\n'
            md += '<tbody>\n'
            md += f'<tr class="row-even"><td>Capital Vida Total (Bruto)</td><td>{ad["capital_vida_total_uf"]:,.0f} UF</td></tr>\n'
            md += f'<tr class="row-odd"><td>Deuda Hipotecaria Total</td><td>{ad["deuda_total_uf"]:,.0f} UF</td></tr>\n'
            md += f'<tr class="row-even"><td><b>Capital Líquido Familiar</b> (Real)</td><td class="highlight-val">{ad["liquidez_familiar_uf"]:,.0f} UF</td></tr>\n'
            md += f'<tr class="row-odd"><td>Brecha Sucesoria Proyectada (4%)</td><td class="highlight-val">{ad["brecha_sucesoria_uf"]:,.0f} UF</td></tr>\n'
            deficit_class = "highlight-deficit" if ad["tiene_deficit"] else "highlight-net"
            deficit_lbl = "Déficit Patrimonial / Descalce" if ad["tiene_deficit"] else "Superávit de Protección"
            md += f'<tr class="row-even"><td><b>{deficit_lbl}</b></td><td class="{deficit_class}">{ad["deficit_sucesorio_uf"]:,.0f} UF</td></tr>\n'
            md += '</tbody></table>\n\n'
            
            if ad["tiene_deficit"] or ad["liquidez_familiar_uf"] == 0:
                md += f"<div class='alert-danger'><b>🚨 Riesgo de Liquidez Sucesoria:</b> {ad['diag_proteccion']}</div>\n\n"
            else:
                md += f"<div class='tax-callout' style='border-left: 4px solid #28a745;'><b>✅ Protección Familiar:</b> {ad['diag_proteccion']}</div>\n\n"
                
            if ad.get('diag_duplicidad') and "No se detecta" not in ad['diag_duplicidad']:
                md += f"<div class='tax-callout' style='border-left: 4px solid #ffc107;'><b>🔍 Duplicidad y Dispersión:</b> {ad['diag_duplicidad']}</div>\n\n"
            
            md += f"<div class='callout-principal'><b>💼 Propuesta de Canje y Reestructuración con PRINCIPAL:</b> {ad['dictamen']}</div>\n\n"
        else:
            md += "> *No se han registrado pólizas para auditar.*\n\n"
            
        md += "---\n\n"


    if combinadas:
        for key, df in carteras.items():
            nombre = key.replace("_", " ").title()
            aum = df['NUEVO_TOTAL'].sum() if not df.empty else 0
            md += f"## Portafolio: {nombre}\n\n"
            md += f"**Activos Totales (AUM):** ${aum:,.0f}\n\n"
            if not df.empty:
                cols = ['PRODUCTO', 'N° CUOTAS', 'NUEVO_PRECIO', 'FECHA_PRECIO', 'NUEVO_TOTAL']
                cols = [c for c in cols if c in df.columns]
                md += df[cols].to_markdown(index=False)
            md += "\n\n<pdf:nextpage />\n\n"
    else:
        if llave_especifica and llave_especifica in carteras:
            df = carteras[llave_especifica]
            nombre = llave_especifica.replace("_", " ").title()
            aum = df['NUEVO_TOTAL'].sum() if not df.empty else 0
            md += f"## Portafolio: {nombre}\n\n"
            md += f"**Activos Totales (AUM):** ${aum:,.0f}\n\n"
            if not df.empty:
                cols = ['PRODUCTO', 'N° CUOTAS', 'NUEVO_PRECIO', 'FECHA_PRECIO', 'NUEVO_TOTAL']
                cols = [c for c in cols if c in df.columns]
                md += df[cols].to_markdown(index=False)
            md += "\n\n"
    return md


def render_capture_360():
    if 'reporte_360_data' not in st.session_state:
        st.session_state['reporte_360_data'] = {'propiedades': [], 'inversiones': [], 'flujo_sucesorio': None, 'current_rut': None}
        
    d = st.session_state['reporte_360_data']

    st.markdown("### 🛠️ Captura de Datos: Reporte 360°")
    st.write("Agrega información cualitativa y cuantitativa para enriquecer el informe ejecutivo final.")
    
    st.markdown("---")
    if st.session_state.get("b2b_authenticated", False):
        st.info(f"🔹 **Modo Integrado:** Sincronizado automáticamente con **{d.get('current_rut', '')}**")
        rut_input = d.get('current_rut')
        col_rut, col_save = st.columns([3, 1])
        with col_save:
            if st.button("💾 Guardar Cambios"):
                save_client_data_from_session()
    else:
        col_rut, col_load, col_save = st.columns([2, 1, 1])
        with col_rut:
            rut_input = st.text_input("RUT del Cliente (Sincronización BD)", value=d.get('current_rut') or "")
        with col_load:
            st.write("") # espaciador
            st.write("")
            if st.button("⬇️ Cargar Datos"):
                if rut_input:
                    load_client_data_to_session(rut_input)
                    st.rerun()
                else:
                    st.warning("Ingrese un RUT.")
        with col_save:
            st.write("") # espaciador
            st.write("")
            if st.button("💾 Guardar Patrimoniales"):
                if rut_input:
                    st.session_state['reporte_360_data']['current_rut'] = rut_input
                    save_client_data_from_session()
                else:
                    st.warning("Ingrese un RUT.")
    st.markdown("---")
    
    with st.expander("🏢 Desglose Inmobiliario Detallado"):
        with st.form("form_inmobiliario", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            nombre_prop = col1.text_input("Nombre / Dirección")
            destino = col2.selectbox("Destino/Uso", ["Habitacional", "Comercial", "Agrícola", "Minero", "Sitio Eriazo"])
            valor_uf = col3.number_input("Valor Comercial (UF)", min_value=0.0, step=500.0)
            
            col4, col5, col6 = st.columns(3)
            arriendo = col4.number_input("Arriendo Percibido (Mensual CLP)", min_value=0.0, step=100000.0)
            dividendo = col5.number_input("Dividendo (Mensual CLP)", min_value=0.0, step=100000.0)
            gastos_comunes = col6.number_input("Gastos Comunes (Mensual CLP)", min_value=0.0, step=10000.0)
            
            col7, col8 = st.columns(2)
            contribuciones = col7.number_input("Contribuciones (Trimestral CLP)", min_value=0.0, step=50000.0)
            seguros = col8.number_input("Seguros Asociados (Mensual CLP)", min_value=0.0, step=10000.0)
            
            if st.form_submit_button("Añadir Propiedad"):
                if nombre_prop:
                    flujo_neto = arriendo - dividendo - gastos_comunes - seguros - (contribuciones / 3)
                    # Asumiendo UF a 38000 para el cap rate rápido
                    valor_clp = valor_uf * 38000
                    cap_rate = ((arriendo * 12) / valor_clp * 100) if valor_clp > 0 else 0
                    
                    d['propiedades'].append({
                        'nombre': nombre_prop, 'destino': destino, 'valor_uf': valor_uf,
                        'arriendo': arriendo, 'dividendo': dividendo, 'gastos_comunes': gastos_comunes,
                        'contribuciones': contribuciones, 'seguros': seguros,
                        'flujo_neto': flujo_neto, 'cap_rate': cap_rate
                    })
                    st.success(f"Propiedad {nombre_prop} añadida.")
                    
        if d['propiedades']:
            st.write("#### Propiedades Registradas:")
            for idx, p in enumerate(d['propiedades']):
                st.info(f"{idx+1}. **{p['nombre']}** | Flujo Neto: ${p['flujo_neto']:,.0f} | Cap Rate: {p['cap_rate']:.2f}%")
            if st.button("Limpiar Propiedades"):
                d['propiedades'] = []
                st.rerun()

    with st.expander("📈 Enriquecimiento de Inversiones"):
        with st.form("form_inversiones", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nombre_inv = col1.text_input("Institución / Nombre de Portafolio")
            tipo_activo = col2.selectbox("Tipo de Activo", ["Renta Fija", "Renta Variable", "Mixto", "Alternativos", "Private Equity"])
            
            col3, col4, col5 = st.columns(3)
            riesgo = col3.selectbox("Nivel de Riesgo", ["Bajo (Conservador)", "Medio (Moderado)", "Alto (Agresivo)"])
            moneda = col4.selectbox("Moneda", ["CLP", "USD", "EUR", "UF"])
            monto = col5.number_input("Monto Actual", min_value=0.0, step=1000000.0)
            
            col6, col7 = st.columns(2)
            tir = col6.number_input("Retorno/TIR Proyectada Anual (%)", format="%.2f")
            rentabilidad = col7.number_input("Rentabilidad Acumulada (%)", format="%.2f")
            
            if st.form_submit_button("Añadir Inversión"):
                if nombre_inv:
                    d['inversiones'].append({
                        'nombre': nombre_inv, 'tipo': tipo_activo, 'riesgo': riesgo,
                        'moneda': moneda, 'monto': monto, 'tir': tir, 'rentabilidad': rentabilidad
                    })
                    st.success(f"Inversión {nombre_inv} añadida.")
                    
        if d['inversiones']:
            st.write("#### Inversiones Registradas:")
            for idx, inv in enumerate(d['inversiones']):
                st.info(f"{idx+1}. **{inv['nombre']}** | Monto: ${inv['monto']:,.0f} | TIR: {inv['tir']}%")
            if st.button("Limpiar Inversiones"):
                d['inversiones'] = []
                st.rerun()

    with st.expander("💼 Flujo de Caja y Sobrevivencia Sucesoria"):
        with st.form("form_flujo_sucesorio"):
            flujo_actual = d.get('flujo_sucesorio') or {}
            st.write("Ingresa los montos **mensuales** aproximados para mantener el estándar de vida del grupo familiar.")
            col1, col2 = st.columns(2)
            gastos_vida = col1.number_input("Gastos de Vida y Familia (Alimentación, colegios, salud)", min_value=0.0, step=500000.0, value=float(flujo_actual.get('gastos_vida', 0.0)))
            sueldos = col2.number_input("Sueldos y Servicios Domésticos (Asesora, jardinero, chofer)", min_value=0.0, step=100000.0, value=float(flujo_actual.get('sueldos', 0.0)))
            
            col3, col4 = st.columns(2)
            compromisos = col3.number_input("Compromisos Fijos (Prorrateo patentes, contribuciones totales)", min_value=0.0, step=100000.0, value=float(flujo_actual.get('compromisos', 0.0)))
            seguros = col4.number_input("Seguros Generales y de Vida vigentes", min_value=0.0, step=50000.0, value=float(flujo_actual.get('seguros', 0.0)))
            
            st.markdown("---")
            ingresos_pasivos = st.number_input("Ingresos Pasivos Estimados (Arriendos líquidos, dividendos de acciones)", min_value=0.0, step=500000.0, value=float(flujo_actual.get('ingresos_pasivos', 0.0)))
            
            if st.form_submit_button("Guardar Parámetros Sucesorios"):
                d['flujo_sucesorio'] = {
                    'gastos_vida': gastos_vida,
                    'sueldos': sueldos,
                    'compromisos': compromisos,
                    'seguros': seguros,
                    'ingresos_pasivos': ingresos_pasivos
                }
                st.success("Parámetros sucesorios guardados en sesión.")
                
        if d['flujo_sucesorio']:
            st.success("✅ Flujo de caja sucesorio configurado. Listo para inyectarse en el reporte.")


from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientProfile, ClientPortfolio, ClientProperty
import json

def load_client_data_to_session(rut):
    db = SessionLocal()
    try:
        clean_rut = rut.replace(".", "").replace("-", "").strip()
        fmt_rut = clean_rut[:-1] + "-" + clean_rut[-1].upper() if len(clean_rut) > 1 else clean_rut
        p = db.query(Prospect).filter((Prospect.rut == fmt_rut) | (Prospect.rut == clean_rut) | (Prospect.rut == rut)).first()
        if p:
            props = []
            for prop in p.properties:
                flujo_neto = (prop.arriendo_mensual or 0) - (prop.dividendo_mensual or 0) - (prop.gastos_comunes or 0) - (prop.seguros or 0) - ((prop.contribuciones_anuales or 0) / 3)
                props.append({
                    'id': prop.id,
                    'nombre': prop.direccion or 'Sin nombre',
                    'destino': prop.destino or 'Habitacional',
                    'valor_uf': prop.valor_comercial_estimado or 0.0,
                    'arriendo': prop.arriendo_mensual or 0.0,
                    'dividendo': prop.dividendo_mensual or 0.0,
                    'gastos_comunes': prop.gastos_comunes or 0.0,
                    'contribuciones': prop.contribuciones_anuales or 0.0,
                    'seguros': prop.seguros or 0.0,
                    'flujo_neto': flujo_neto,
                    'cap_rate': prop.cap_rate or 0.0
                })
                
            invs = []
            for inv in p.portfolios:
                invs.append({
                    'id': inv.id,
                    'nombre': inv.institucion or 'Portafolio',
                    'tipo': inv.tipo_activo or 'Mixto',
                    'riesgo': inv.riesgo or 'Medio (Moderado)',
                    'moneda': inv.moneda_original or 'CLP',
                    'monto': inv.monto_original or 0.0,
                    'tir': inv.tir or 0.0,
                    'rentabilidad': inv.rentabilidad or 0.0
                })
                
            flujo = None
            if p.profile and p.profile.flujo_sucesorio:
                try:
                    flujo = json.loads(p.profile.flujo_sucesorio)
                except:
                    pass
                    
            if not flujo:
                flujo = {}
                
            # Asignación automática desde KYC estructurado (Ficha de Cliente)
            if getattr(p, 'gastos_recurrentes', 0) > 0:
                if 'gastos_vida' not in flujo or not flujo['gastos_vida']:
                    flujo['gastos_vida'] = p.gastos_recurrentes / 12
                    
            # Auditoría de seguros
            from src.intelligence.insurance_analyzer import auditar_polizas_cliente
            audit_result = auditar_polizas_cliente(p.id, db)

            st.session_state['reporte_360_data'] = {
                'propiedades': props,
                'inversiones': invs,
                'flujo_sucesorio': flujo,
                'current_rut': rut,
                'intereses_hipotecarios': getattr(p, 'intereses_hipotecario', 0.0) or 0.0,
                'gastos_educacion': getattr(p, 'gastos_educacion', 0.0) or 0.0,
                'retenciones_2da_cat': getattr(p, 'retenciones_2da_cat', 0.0) or 0.0,
                'audit_seguros': audit_result
            }
            st.success(f"Datos de {rut} cargados desde la base de datos.")
        else:
            st.warning("Cliente no encontrado en la base de datos.")
    finally:
        db.close()

def save_client_data_from_session():
    if 'reporte_360_data' not in st.session_state or 'current_rut' not in st.session_state['reporte_360_data']:
        st.error("No hay un cliente seleccionado o datos en memoria para guardar.")
        return
        
    rut = st.session_state['reporte_360_data']['current_rut']
    d = st.session_state['reporte_360_data']
    
    db = SessionLocal()
    try:
        clean_rut = rut.replace(".", "").replace("-", "").strip()
        fmt_rut = clean_rut[:-1] + "-" + clean_rut[-1].upper() if len(clean_rut) > 1 else clean_rut
        p = db.query(Prospect).filter((Prospect.rut == fmt_rut) | (Prospect.rut == clean_rut) | (Prospect.rut == rut)).first()
        if not p:
            st.error("El cliente ya no existe en la base de datos.")
            return
            
        if not p.profile:
            p.profile = ClientProfile(prospect_id=p.id)
            db.add(p.profile)
            
        if d['flujo_sucesorio']:
            p.profile.flujo_sucesorio = json.dumps(d['flujo_sucesorio'])
            
        for p_data in d.get('propiedades', []):
            if 'id' in p_data and p_data['id']:
                prop = db.query(ClientProperty).filter_by(id=p_data['id']).first()
                if not prop:
                    prop = ClientProperty(prospect_id=p.id)
                    db.add(prop)
            else:
                prop = ClientProperty(prospect_id=p.id)
                db.add(prop)
            
            prop.direccion = p_data.get('nombre', '')
            prop.destino = p_data.get('destino', '')
            prop.valor_comercial_estimado = p_data.get('valor_uf', 0.0)
            prop.arriendo_mensual = p_data.get('arriendo', 0.0)
            prop.dividendo_mensual = p_data.get('dividendo', 0.0)
            prop.gastos_comunes = p_data.get('gastos_comunes', 0.0)
            prop.contribuciones_anuales = p_data.get('contribuciones', 0.0)
            prop.seguros = p_data.get('seguros', 0.0)
            prop.cap_rate = p_data.get('cap_rate', 0.0)
            
        for i_data in d.get('inversiones', []):
            if 'id' in i_data and i_data['id']:
                inv = db.query(ClientPortfolio).filter_by(id=i_data['id']).first()
                if not inv:
                    inv = ClientPortfolio(prospect_id=p.id)
                    db.add(inv)
            else:
                inv = ClientPortfolio(prospect_id=p.id)
                db.add(inv)
                
            inv.institucion = i_data.get('nombre', '')
            inv.tipo_activo = i_data.get('tipo', '')
            inv.riesgo = i_data.get('riesgo', '')
            inv.moneda_original = i_data.get('moneda', '')
            inv.monto_original = i_data.get('monto', 0.0)
            inv.tir = i_data.get('tir', 0.0)
            inv.rentabilidad = i_data.get('rentabilidad', 0.0)
            
        db.commit()
        st.success("✅ Datos Patrimoniales del Cliente guardados correctamente en la base de datos.")
    except Exception as e:
        db.rollback()
        st.error(f"Error al guardar datos: {e}")
    finally:
        db.close()


def render_report_generator_ui():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0A2342 0%, #001229 100%); padding: 25px; border-radius: 10px; margin-bottom: 25px; color: white; border-left: 5px solid #D4AF37;'>
            <h1 style='color: white; margin: 0; font-size: 2.2em;'>📄 Generador de Informes (PDF)</h1>
            <p style='margin: 10px 0 0 0; font-size: 1.1em; color: #e2e8f0;'>
                Captura métricas patrimoniales 360° y genera los informes ejecutivos finales para tus clientes.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 1. Captura Patrimonial 360°", "🖨️ 2. Generar Reporte PDF"])
    
    with tab1:
        render_capture_360()
        
    with tab2:
        # Ver si hay carteras en memoria
        hay_carteras = 'carteras_recalculadas' in st.session_state and st.session_state.carteras_recalculadas
        
        modo = st.radio("Modo de Generación", ["Manual (Escribir Markdown)", "Automático (Desde Portafolios Activos + 360)"], index=1 if hay_carteras else 0)
        
        if modo == "Automático (Desde Portafolios Activos + 360)":
            if not hay_carteras:
                st.warning("No hay portafolios procesados en memoria. Ve a la sección 'Estrategia & Cartolas' y luego 'Valuación' para cargar uno.")
                if 'reporte_360_data' in st.session_state and (st.session_state['reporte_360_data']['propiedades'] or st.session_state['reporte_360_data']['inversiones'] or st.session_state['reporte_360_data']['flujo_sucesorio']):
                    st.info("Sin embargo, detectamos datos 360° capturados. Puedes generar un reporte solo con esta información.")
                    if st.button("🚀 Generar Reporte 360°", type="primary"):
                        with st.spinner("Compilando reporte 360..."):
                            texto = auto_generate_markdown({})
                            pdf_bytes = generate_reporte_360_from_markdown(texto, "Reporte Patrimonial 360°")
                            
                            # Generate DOCX
                            docx_path = os.path.join(tempfile.gettempdir(), f"Reporte_Consolidado_360_{st.session_state['reporte_360_data'].get('current_rut', 'S-RUT')}.docx")
                            generar_docx_reporte_360(st.session_state['reporte_360_data'], docx_path)
                            
                            if pdf_bytes and os.path.exists(docx_path):
                                st.success("✅ Generación exitosa. Secciones incluidas: Inmobiliario, Inversiones, Flujo Sucesorio.")
                                
                                col_pdf, col_docx = st.columns(2)
                                col_pdf.download_button("📥 Descargar PDF 360", data=pdf_bytes, file_name="Reporte_Consolidado_360.pdf", mime="application/pdf")
                                
                                with open(docx_path, "rb") as f:
                                    docx_bytes = f.read()
                                
                                rut_file = str(st.session_state['reporte_360_data'].get('current_rut') or 'N-A').replace('.', '').replace('-', '')
                                col_docx.download_button("📝 Descargar Reporte 360 en Word (.docx)", data=docx_bytes, file_name=f"Reporte_Consolidado_360_{rut_file}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                                
                                # Clean up
                                try:
                                    os.remove(docx_path)
                                except:
                                    pass
                            else:
                                st.error("Error al generar los documentos.")
                return
                
            tipo_informe = st.radio("Agrupación del Informe", ["Consolidado (Todas las entidades en un PDF)", "Separado por RUT/Entidad"])
            
            if tipo_informe == "Consolidado (Todas las entidades en un PDF)":
                st.info("Se generará un único documento PDF con capítulos separados para cada RUT/Entidad.")
                if st.button("🚀 Generar y Descargar Informe Consolidado", type="primary"):
                    with st.spinner("Compilando reporte..."):
                        texto = auto_generate_markdown(st.session_state.carteras_recalculadas, combinadas=True)
                        pdf_bytes = generar_pdf_bytes("Informe Estratégico Consolidado", texto)
                        if pdf_bytes:
                            st.download_button("📥 Descargar PDF Consolidado", data=pdf_bytes, file_name="Reporte_Consolidado.pdf", mime="application/pdf")
                        else:
                            st.error("Error al generar el PDF.")
            else:
                st.info("Se generarán PDFs individuales para cada entidad.")
                for key in st.session_state.carteras_recalculadas.keys():
                    col1, col2 = st.columns([3, 1])
                    nombre = key.replace("_", " ").title()
                    col1.write(f"**{nombre}**")
                    
                    texto = auto_generate_markdown(st.session_state.carteras_recalculadas, combinadas=False, llave_especifica=key)
                    pdf_bytes = generar_pdf_bytes(f"Informe Estratégico: {nombre}", texto)
                    
                    if pdf_bytes:
                        col2.download_button(f"📥 Descargar PDF", data=pdf_bytes, file_name=f"Reporte_{key}.pdf", mime="application/pdf", key=f"btn_dl_{key}")

        else:
            titulo_informe = st.text_input("Título del Informe", "Informe Ejecutivo: Análisis Estratégico")
            
            # Pre-poblamos el area de texto con lo que haya del 360 para que sea editable
            pre_markdown = auto_generate_markdown({}, combinadas=False) if 'reporte_360_data' in st.session_state else ""
            
            texto_markdown = st.text_area("Contenido del Informe (Soporta Markdown)", value=pre_markdown, height=400, placeholder="Escribe o pega aquí el análisis...")
            nombre_archivo = st.text_input("Nombre del archivo de salida (asegúrate de incluir .pdf)", "Reporte_Altus.pdf")
            
            if texto_markdown.strip():
                texto_procesado = texto_markdown.replace("---", "<pdf:nextpage />")
                pdf_bytes = generar_pdf_bytes(titulo_informe, texto_procesado)
                
                if pdf_bytes:
                    st.download_button(
                        label="🚀 Descargar PDF Institucional",
                        data=pdf_bytes,
                        file_name=nombre_archivo if nombre_archivo.endswith('.pdf') else nombre_archivo + '.pdf',
                        mime="application/pdf",
                        width="stretch",
                        type="primary"
                    )
                else:
                    st.error("Hubo un error al compilar el documento PDF internamente.")
            else:
                st.info("Escribe contenido en la caja de arriba para habilitar el botón de descarga.")
