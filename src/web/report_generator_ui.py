import streamlit as st
import os
import importlib
import generador_informes
importlib.reload(generador_informes)
from generador_informes import generar_pdf_bytes

def auto_generate_markdown(carteras, combinadas=True, llave_especifica=None):
    md = ""
    
    # Inyectar las notas estratégicas si fueron provistas en el auditor
    notas = st.session_state.get('notas_estrategicas_auditor', '').strip()
    if notas:
        md += "## 🧠 Tesis de Reestructuración & Estrategia\n\n"
        md += f"> *{notas}*\n\n---\n\n"
        
    if combinadas:
        for key, df in carteras.items():
            nombre = key.replace("_", " ").title()
            aum = df['NUEVO_TOTAL'].sum() if not df.empty else 0
            md += f"## Portafolio: {nombre}\n\n"
            md += f"**Activos Totales (AUM):** ${aum:,.0f}\\n\\n"
            if not df.empty:
                cols = ['PRODUCTO', 'N° CUOTAS', 'NUEVO_PRECIO', 'FECHA_PRECIO', 'NUEVO_TOTAL']
                cols = [c for c in cols if c in df.columns]
                md += df[cols].to_markdown(index=False)
            md += "\\n\\n<pdf:nextpage />\\n\\n"
    else:
        if llave_especifica and llave_especifica in carteras:
            df = carteras[llave_especifica]
            nombre = llave_especifica.replace("_", " ").title()
            aum = df['NUEVO_TOTAL'].sum() if not df.empty else 0
            md += f"## Portafolio: {nombre}\\n\\n"
            md += f"**Activos Totales (AUM):** ${aum:,.0f}\\n\\n"
            if not df.empty:
                cols = ['PRODUCTO', 'N° CUOTAS', 'NUEVO_PRECIO', 'FECHA_PRECIO', 'NUEVO_TOTAL']
                cols = [c for c in cols if c in df.columns]
                md += df[cols].to_markdown(index=False)
            md += "\\n\\n"
    return md

def render_report_generator_ui():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0A2342 0%, #001229 100%); padding: 25px; border-radius: 10px; margin-bottom: 25px; color: white; border-left: 5px solid #D4AF37;'>
            <h1 style='color: white; margin: 0; font-size: 2.2em;'>📄 Generador de Informes (PDF)</h1>
            <p style='margin: 10px 0 0 0; font-size: 1.1em; color: #e2e8f0;'>
                Genera los informes ejecutivos finales para tus clientes.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Ver si hay carteras en memoria
    hay_carteras = 'carteras_recalculadas' in st.session_state and st.session_state.carteras_recalculadas
    
    modo = st.radio("Modo de Generación", ["Manual (Escribir Markdown)", "Automático (Desde Portafolios Activos)"], index=1 if hay_carteras else 0)
    
    if modo == "Automático (Desde Portafolios Activos)":
        if not hay_carteras:
            st.warning("No hay portafolios procesados en memoria. Ve a la sección 'Estrategia & Cartolas' y luego 'Valuación' para cargar uno.")
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
        texto_markdown = st.text_area("Contenido del Informe (Soporta Markdown)", height=400, placeholder="Escribe o pega aquí el análisis...")
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
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.error("Hubo un error al compilar el documento PDF internamente.")
        else:
            st.info("Escribe contenido en la caja de arriba para habilitar el botón de descarga.")
