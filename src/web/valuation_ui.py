import streamlit as st
import pandas as pd
from sura_excel_parser import parse_sura_excel
from portfolio_pricer import fetch_market_prices

def render_valuation_ui():
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0A2342 0%, #001229 100%); padding: 25px; border-radius: 10px; margin-bottom: 25px; color: white; border-left: 5px solid #D4AF37;'>
            <h1 style='color: white; margin: 0; font-size: 2.2em;'>📈 Actualización de Valores de Portafolio</h1>
            <p style='margin: 10px 0 0 0; font-size: 1.1em; color: #e2e8f0;'>
                El robot de ALTUS AI buscará los precios de mercado en tiempo real. 
                Si algún fondo mutuo o activo no está listado en bolsa pública, puedes ingresar su valor cuota manualmente.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📥 Actualización Global de Precios CMF")
    st.write("Esta sección actualiza la base de datos maestra de Altus AI con los valores cuota de todos los fondos mutuos de Chile.")
    tab1, tab2 = st.tabs(["🤖 Robot Automático", "🖐️ Carga Manual (Recomendado)"])
    
    with tab1:
        st.write("Intenta descargar automáticamente el archivo de la CMF. Puede ser bloqueado por seguridad (WAF).")
        if st.button("🔄 Ejecutar Robot de Extracción"):
            with st.spinner("Conectando con servidores de la CMF..."):
                import sys
                import os
                base_path = os.path.abspath(os.curdir)
                if base_path not in sys.path:
                    sys.path.insert(0, base_path)
                
                import subprocess
                try:
                    # Elimina archivo anterior si existe para evitar falsos positivos
                    if os.path.exists("data/raw/fm_valor_cuota.zip"):
                        os.remove("data/raw/fm_valor_cuota.zip")
                    
                    subprocess.run([sys.executable, "src/osint/spider_cmf_zip.py"], capture_output=True, text=True)
                    
                    if os.path.exists("data/raw/fm_valor_cuota.zip"):
                        from src.osint.cmf_zip_ingestor import CMFZipIngestor
                        ingestor = CMFZipIngestor("data/raw/fm_valor_cuota.zip")
                        res = ingestor.run_ingestion()
                        if res['exito']:
                            st.success("¡Base de datos actualizada exitosamente con el Robot Automático!")
                            if 'precios_mercado' in st.session_state:
                                del st.session_state['precios_mercado']
                            st.rerun()
                        else:
                            st.error(res['mensaje'])
                    else:
                        st.error("❌ El robot fue bloqueado por la CMF. Por favor usa la opción de Carga Manual.")
                except Exception as e:
                    st.error(f"Error al ejecutar el robot: {e}")

    with tab2:
        st.markdown("Si la CMF bloquea al robot, usa este método infalible:")
        st.markdown("1. Ingresa a la CMF haciendo clic aquí: [**Descargar Valor Cuota CMF**](https://www.cmfchile.cl/institucional/estadisticas/fm.bpr_menu.php)")
        st.markdown("2. Descarga el archivo de ayer (botón Descargar, bajará un archivo `.zip` o `.xlsx`).")
        st.markdown("3. Arrastra y suelta el archivo aquí:")
        uploaded_file = st.file_uploader("Sube el archivo de la CMF (.zip o .xlsx)", type=["zip", "xlsx", "xls"])
        
        if uploaded_file is not None:
            import os
            os.makedirs("data/raw", exist_ok=True)
            
            # Usar el nombre original o uno genérico si falla
            file_ext = os.path.splitext(uploaded_file.name)[1]
            file_path = f"data/raw/fm_valor_cuota{file_ext}"
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Procesando archivo CMF manual..."):
                import sys
                base_path = os.path.abspath(os.curdir)
                if base_path not in sys.path:
                    sys.path.insert(0, base_path)
                from src.osint.cmf_zip_ingestor import CMFZipIngestor
                ingestor = CMFZipIngestor(file_path)
                res = ingestor.run_ingestion()
                
                if res['exito']:
                    st.success("✅ ¡Base de datos maestra actualizada correctamente desde tu archivo!")
                    if 'precios_mercado' in st.session_state:
                        del st.session_state['precios_mercado']
                    st.rerun()
                else:
                    st.error(res['mensaje'])
                    
    st.markdown("---")
    
    if 'carteras' not in st.session_state:
        st.warning("⚠️ No se ha cargado ninguna cartera de cliente para valorar. Por favor, sube y procesa un archivo Excel en la sección 'Estrategia & Cartolas' primero.")
        
        def nav_to_cartolas():
            st.session_state.sub_nav_auditoria = "Estrategia & Cartolas"
            
        st.button("⬅️ Ir a Estrategia & Cartolas", on_click=nav_to_cartolas)
        return

    if 'precios_mercado' not in st.session_state:
        df_raw = st.session_state.carteras['raw_cleaned']
        productos_unicos = df_raw['PRODUCTO'].dropna().unique().tolist()
        with st.spinner("Conectando con Yahoo Finance y Base CMF para buscar precios en tiempo real..."):
            st.session_state.precios_mercado = fetch_market_prices(productos_unicos)
            
    st.title("🤖 Smart Pricing Engine del Cliente")
    st.write("Verifica y completa los valores cuota / precios actuales de la cartera cargada. Los campos pre-llenados fueron obtenidos directamente desde la Bolsa de Santiago o la Base de Datos Maestra CMF.")
    
    precios = st.session_state.precios_mercado
    
    with st.form("pricing_form"):
        nuevos_precios = {}
        for prod, data in precios.items():
            if data is not None and isinstance(data, dict):
                precio_sugerido = data['precio']
                fecha = data.get('fecha', 'Reciente')
                valor = st.number_input(f"✅ {prod} (Obtenido de Mercado al {fecha})", value=float(precio_sugerido), format="%.2f")
            elif data is not None:
                # Legacy support
                valor = st.number_input(f"✅ {prod} (Obtenido de Mercado)", value=float(data), format="%.2f")
            else:
                # No lo encontró
                st.markdown(f"**⚠️ {prod}**")
                valor = st.number_input(f"Ingresar Valor Cuota manual para {prod}:", value=0.0, format="%.4f")
                
            nuevos_precios[prod] = valor
            
        submit = st.form_submit_button("💾 Aplicar Precios y Recalcular Portafolio", type="primary")
            
        if submit:
            st.session_state.precios_actualizados = nuevos_precios
            st.success("¡Precios actualizados con éxito!")
            
            # Recalcular las 3 carteras
            # Recalcular todas las carteras dinámicamente
            def aplicar_recalculo(df):
                if df.empty: return df
                df['NUEVO_PRECIO'] = df['PRODUCTO'].map(nuevos_precios)
                df['NUEVO_TOTAL'] = df['N° CUOTAS'] * df['NUEVO_PRECIO']
                
                # Obtener la fecha de precios_mercado si existe
                def get_fecha(prod):
                    data = st.session_state.precios_mercado.get(prod)
                    if isinstance(data, dict):
                        return data.get('fecha', 'Reciente')
                    return 'Manual/No Registrada'
                
                df['FECHA_PRECIO'] = df['PRODUCTO'].apply(get_fecha)
                
                # Fallback: Si no hay N° CUOTAS (ej. Pershing, saldos fijos) o el nuevo total es nulo
                mask = df['NUEVO_TOTAL'].isna() | (df['NUEVO_TOTAL'] == 0)
                if 'TOTAL ACTUALIZADO' in df.columns:
                    df.loc[mask, 'NUEVO_TOTAL'] = df.loc[mask, 'TOTAL ACTUALIZADO']
                    
                return df
                
            carteras_recalculadas = {}
            for key, df_subset in st.session_state.carteras.items():
                if key != "raw_cleaned":
                    carteras_recalculadas[key] = aplicar_recalculo(df_subset.copy())
            
            # Auto-save en el filesystem
            import os
            os.makedirs("data/portfolios_historicos", exist_ok=True)
            for key, df_rec in carteras_recalculadas.items():
                safe_name = "".join([c if c.isalnum() else "_" for c in key])
                df_rec.to_csv(f"data/portfolios_historicos/{safe_name}_updated.csv", index=False)
            
            # Auto-save en el session_state para que la App.py lo capture
            opciones_auditor = {}
            for key, df_rec in carteras_recalculadas.items():
                label = key.replace("_", " ").title()
                total_aum = float(df_rec['NUEVO_TOTAL'].sum()) if not df_rec.empty else 0.0
                opciones_auditor[label] = total_aum
                
            st.session_state.opciones_auditor = opciones_auditor
            st.session_state.carteras_recalculadas = carteras_recalculadas
                
            st.markdown("---")
            st.subheader("🏦 Resultados del Recálculo (AUM Consolidado al día de hoy)")
            
            # Crear columnas dinámicas para mostrar los AUM
            cols = st.columns(len(carteras_recalculadas))
            
            for i, (key, df_rec) in enumerate(carteras_recalculadas.items()):
                total_aum = df_rec['NUEVO_TOTAL'].sum() if not df_rec.empty else 0
                label = key.replace("_", " ").title()
                cols[i].metric(label, f"${total_aum:,.0f}")
                
            st.info("✅ Precios actualizados y portafolio guardado automáticamente. Puedes pasar a la siguiente fase.")
            
            def nav_to_auditor():
                st.session_state.sub_nav_auditoria = "Auditor de Portafolio"

            st.button("➡️ Siguiente Fase: Comparativa Comercial", on_click=nav_to_auditor, type="primary", use_container_width=True)
