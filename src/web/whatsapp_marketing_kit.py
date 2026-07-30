import streamlit as st
import os
import base64
import asyncio

def render_whatsapp_kit_ui():
    st.markdown("### 📱 Kit de Marketing & Comunicación Profesional para WhatsApp Business")
    st.info("Herramientas diseñadas para maximizar la presencia de marca de **FV Asesorías e Inversiones** en WhatsApp: foto de perfil optimizada para círculo, estados verticales 9:16, tarjetas de catálogo y plantillas con firmas profesionales.")
    st.write("")

    w_subtab1, w_subtab2, w_subtab3, w_subtab4 = st.tabs([
        "🖼️ Foto de Perfil Oficial (Círculo Safe Zone)",
        "📱 Generador de Estados (Vertical 9:16)",
        "💼 Catálogo de Servicios (Tarjetas 1:1)",
        "✍️ Firma Profesional & Mensajería"
    ])

    # -------------------------------------------------------------
    # SUBTAB 1: FOTO DE PERFIL OFICIAL (AJUSTADA AL CÍRCULO)
    # -------------------------------------------------------------
    with w_subtab1:
        st.markdown("#### 🖼️ Foto de Perfil Optimizada para WhatsApp Business")
        st.caption("WhatsApp recorta automáticamente las imágenes de perfil en formato circular. Esta versión ubica el emblema **FV**, el texto de marca y la acreditación **ALTUS AI** dentro de la 'zona segura' circular sin cortes.")

        avatar_path = os.path.join(os.getcwd(), "assets", "whatsapp", "perfil_whatsapp_fv_oficial.png")
        
        col_av1, col_av2 = st.columns([1, 1])
        with col_av1:
            if os.path.exists(avatar_path):
                st.image(avatar_path, caption="Foto de Perfil Oficial FV (1080x1080px - Círculo Centrado)", use_container_width=True)
            else:
                st.warning("Foto de perfil no encontrada. Haz clic abajo para generarla.")
        
        with col_av2:
            st.markdown("""
            ##### 🎯 Recomendaciones de Implementación:
            1. **Guardar en el teléfono:** Descarga la imagen usando el botón inferior.
            2. **Subir a WhatsApp Business:** Ve a *Ajustes* > *Perfil de la Empresa* > *Editar foto*.
            3. **Ajuste automático:** El anillo dorado perimetral sirve como guía exacta para el visor de WhatsApp. Al centrarlo, la marca quedará alineada y legible.
            """)
            st.write("")
            if os.path.exists(avatar_path):
                with open(avatar_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar Foto de Perfil (HD PNG)",
                        data=file,
                        file_name="FV_Perfil_Oficial_WhatsApp.png",
                        mime="image/png",
                        type="primary",
                        use_container_width=True
                    )

    # -------------------------------------------------------------
    # SUBTAB 2: GENERADOR DE ESTADOS DE WHATSAPP (VERTICAL 9:16)
    # -------------------------------------------------------------
    with w_subtab2:
        st.markdown("#### 📱 Generador de Estados / Stories de WhatsApp (1080x1920px - 9:16)")
        st.caption("Crea diapositivas verticales institucionales para compartir en tus estados de WhatsApp. Captura la atención de prospectos con datos duros y llamados a la acción claros.")

        st_tema = st.selectbox("Selecciona la plantilla de contenido:", [
            "💡 APV & Beneficios Fiscales (Régimen A y B)",
            "📑 Reliquidación Tributaria (Devolución Impuestos CMF)",
            "🏡 Inversión Inmobiliaria vs Renta Fija / Variable",
            "📊 Resumen de Mercado & Dólar Observado CLP",
            "✍️ Tema Personalizado"
        ])

        if st_tema == "💡 APV & Beneficios Fiscales (Régimen A y B)":
            p_title = "APV & Optimización Tributaria"
            p_topic = "Estrategia Previsional 2026"
            p_b1 = "Gana hasta 15% de Bonificación Fiscal Directa del Estado (Régimen A)."
            p_b2 = "Rebaja hasta 54 UF anuales de tu Impuesto Global Complementario (Régimen B)."
            p_b3 = "Combina ambos regímenes para maximizar la rentabilidad de tus excedentes."
            p_cta = "Escríbeme por WhatsApp para evaluar tu tramo tributario sin costo."
        elif st_tema == "📑 Reliquidación Tributaria (Devolución Impuestos CMF)":
            p_title = "Reliquidación Tributaria CMF / SII"
            p_topic = "Recuperación de Impuestos"
            p_b1 = "Recupera retenciones por créditos hipotecarios (Art. 55 bis del DLI)."
            p_b2 = "Aprovecha la devolución de excesos por aportes a APV y seguros."
            p_b3 = "Proceso auditado sin riesgos ante el Servicio de Impuestos Internos."
            p_cta = "Solicita tu revisión de reliquidación tributaria directamente."
        elif st_tema == "🏡 Inversión Inmobiliaria vs Renta Fija / Variable":
            p_title = "Crédito Hipotecario vs Inversión"
            p_topic = "Arbitraje de Tasas & Deuda"
            p_b1 = "Compara el retorno real del pie inmobiliario vs instrumentos financieros."
            p_b2 = "Evalúa la holgura financiera antes de comprometer liquidez."
            p_b3 = "Simulación cuantitativa 4K personalizada para tu perfil."
            p_cta = "Pide tu simulación comparativa de inversión."
        elif st_tema == "📊 Resumen de Mercado & Dólar Observado CLP":
            p_title = "Inteligencia de Mercado Global"
            p_topic = "Coyuntura Macroeconómica"
            p_b1 = "Monitoreo diario del tipo de cambio USD/CLP e IPSA."
            p_b2 = "Impacto de las decisiones de tasas de la FED y el Banco Central de Chile."
            p_b3 = "Estrategias defensivas en Renta Fija y Coberturas Cambiarias."
            p_cta = "Conversemos sobre la mejor distribución para tu portafolio."
        else:
            p_topic = st.text_input("Etiqueta / Tema Superior:", "Estrategia Patrimonial")
            p_title = st.text_input("Título Principal del Estado:", "Optimizando tu Patrimonio")
            p_b1 = st.text_input("Punto 1:", "Punto relevante 1 sobre la estrategia")
            p_b2 = st.text_input("Punto 2:", "Punto relevante 2 sobre el mercado")
            p_b3 = st.text_input("Punto 3:", "Punto relevante 3 con llamado a la acción")
            p_cta = st.text_input("Llamado a la Acción (CTA):", "Escríbeme por WhatsApp para más detalles.")

        if st.button("🚀 Generar Estado de WhatsApp (9:16 Vertical HD)", type="primary", use_container_width=True, key="btn_gen_wa_state"):
            with st.spinner("🖼️ Renderizando diapositiva vertical 1080x1920px con Playwright..."):
                try:
                    from scripts.generate_whatsapp_state_slide import generate_whatsapp_state
                    out_filename = "estado_whatsapp_generado.png"
                    asyncio.run(generate_whatsapp_state(
                        title=p_title,
                        topic=p_topic,
                        bullet1=p_b1,
                        bullet2=p_b2,
                        bullet3=p_b3,
                        cta=p_cta,
                        filename=out_filename
                    ))
                    st.session_state["wa_state_img_path"] = os.path.join(os.getcwd(), "assets", "whatsapp_status", out_filename)
                    st.success("✅ ¡Estado de WhatsApp generado exitosamente!")
                except Exception as e:
                    st.error(f"Error al generar el estado: {str(e)}")

        if "wa_state_img_path" in st.session_state and os.path.exists(st.session_state["wa_state_img_path"]):
            st.markdown("---")
            st.markdown("##### 📸 Vista Previa del Estado de WhatsApp (1080x1920px):")
            col_preview, col_down = st.columns([1, 1])
            with col_preview:
                st.image(st.session_state["wa_state_img_path"], use_container_width=True)
            with col_down:
                st.info("💡 **Tip para WhatsApp:** Guarda la imagen en la galería de tu teléfono y compártela directamente en *Mi Estado*.")
                with open(st.session_state["wa_state_img_path"], "rb") as f_img:
                    st.download_button(
                        label="⬇️ Descargar Estado de WhatsApp (PNG HD)",
                        data=f_img,
                        file_name="Estado_WhatsApp_FV.png",
                        mime="image/png",
                        type="primary",
                        use_container_width=True
                    )

    # -------------------------------------------------------------
    # SUBTAB 3: CATÁLOGO DE SERVICIOS (TARJETAS 1:1)
    # -------------------------------------------------------------
    with w_subtab3:
        st.markdown("#### 💼 Tarjetas de Servicios para el Catálogo de WhatsApp Business")
        st.caption("Imágenes cuadradas (1080x1080px) diseñadas específicamente para añadir en la sección **Catálogo** de WhatsApp Business.")

        cat_dir = os.path.join(os.getcwd(), "assets", "whatsapp_catalog")
        
        cards_info = [
            {"file": "catalogo_1_apv.png", "title": "1. Asesoría en APV & Tributación", "name": "Catalog_APV_FV.png"},
            {"file": "catalogo_2_reliquidacion.png", "title": "2. Reliquidación Tributaria", "name": "Catalog_Reliquidacion_FV.png"},
            {"file": "catalogo_3_inmobiliario.png", "title": "3. Créditos vs Inversión", "name": "Catalog_Inmobiliario_FV.png"},
            {"file": "catalogo_4_family_office.png", "title": "4. Multi-Family Office & AI", "name": "Catalog_FamilyOffice_FV.png"}
        ]

        grid_c1, grid_c2 = st.columns(2)
        for i, card in enumerate(cards_info):
            target_col = grid_c1 if i % 2 == 0 else grid_c2
            card_path = os.path.join(cat_dir, card["file"])
            with target_col:
                st.markdown(f"##### {card['title']}")
                if os.path.exists(card_path):
                    st.image(card_path, use_container_width=True)
                    with open(card_path, "rb") as f_card:
                        st.download_button(
                            label=f"⬇️ Descargar Tarjeta Catálogo",
                            data=f_card,
                            file_name=card["name"],
                            mime="image/png",
                            key=f"btn_dl_card_{i}",
                            use_container_width=True
                        )
                else:
                    st.warning("Imagen no generada.")
                st.write("")

    # -------------------------------------------------------------
    # SUBTAB 4: FIRMA PROFESIONAL Y PLANTILLAS DE MENSAJERÍA
    # -------------------------------------------------------------
    with w_subtab4:
        st.markdown("#### ✍️ Firmas y Plantillas de Comunicación Profesional")
        
        firm_tab1, firm_tab2 = st.tabs([
            "💬 Mensajes & Firma Formateada para WhatsApp",
            "📧 Código de Firma HTML para Correo Electrónico"
        ])

        with firm_tab1:
            st.markdown("##### 💬 Plantillas de Mensajes Directos para Prospectos y Clientes")
            st.caption("Mensajes redactados con formato enriquecido para WhatsApp (`*negrita*`, viñetas y estructuración ejecutiva). Copia y pega directamente en tu chat.")

            msg_opt = st.selectbox("Selecciona el tipo de mensaje a enviar:", [
                "👋 1. Primer Contacto a Referido / Prospecto",
                "🎯 2. Presentación de Oportunidad APV / Reliquidación",
                "📊 3. Invitación a Revisión de Portafolio / Asesoría",
                "✍️ 4. Firma de Cierre Estándar para WhatsApp"
            ])

            if msg_opt == "👋 1. Primer Contacto a Referido / Prospecto":
                wa_template = """Hola *[Nombre del Cliente]*, muy buenos días.

Te hablo por recomendación de *[Nombre Referidor]*, quien me sugirió ponerme en contacto contigo.

Soy *Francisco Valencia*, Managing Partner en *FV Asesorías e Inversiones*. Nos especializamos en **planificación patrimonial, optimización de impuestos (APV / Reliquidación CMF)** y **gestión de inversiones eficientes** mediante nuestra plataforma de inteligencia *ALTUS AI*.

Cuéntame, ¿a qué hora tienes disponibilidad esta semana para que conversemos brevemente (10 min) por llamada o reunión virtual?

Quedo atento a tus comentarios.

Saludos cordiales,

*Francisco Valencia*
Managing Partner | Asesor Financiero Senior
🏢 *FV Asesorías e Inversiones*
🤖 Powered by *ALTUS AI*
🌐 https://fv-inversiones.com"""

            elif msg_opt == "🎯 2. Presentación de Oportunidad APV / Reliquidación":
                wa_template = """Hola *[Nombre del Cliente]*, ¿cómo estás?

Espero que estés teniendo una excelente semana.

Te escribo para comentarte que estamos realizando la evaluación de **Optimización Tributaria 2026** para nuestros clientes. 

Existen dos oportunidades muy concretas para optimizar tu carga fiscal:
1. **Bonificación Fiscal Directa del 15%** otorgada por el Estado a través del APV Régimen A.
2. **Rebaja de hasta 54 UF** en tu Impuesto Global Complementario a través del Régimen B o devolución de retenciones por dividendos hipotecarios.

Me gustaría ofrecerte una **Evaluación Tributaria y Previsional sin costo** para calcular el impacto exacto en tus impuestos.

¿Te parece si agendamos una llamada de 15 minutos esta semana?

Saludos cordiales,

*Francisco Valencia*
Managing Partner | Asesor Financiero Senior
🏢 *FV Asesorías e Inversiones*
🤖 Powered by *ALTUS AI*"""

            elif msg_opt == "📊 3. Invitación a Revisión de Portafolio / Asesoría":
                wa_template = """Estimado/a *[Nombre del Cliente]*, espero que te encuentres muy bien.

En *FV Asesorías e Inversiones* hemos actualizado nuestras proyecciones de mercado y tasas para este trimestre con nuestro motor de inteligencia *ALTUS AI*.

Nos gustaría invitarte a una sesión de **Revisión de Portafolio & Asignación de Activos**, donde evaluaremos:
• Estrategias de protección ante volatilidad del tipo de cambio (USD/CLP).
• Oportunidades en Renta Fija local e internacional.
• Balance de liquidez y holgura financiera.

¿Tienes disponibilidad este *[Día]* a las *[Hora]* para coordinar nuestra reunión?

Un cordial saludo,

*Francisco Valencia*
Managing Partner | Asesor Financiero Senior
🏢 *FV Asesorías e Inversiones*
🤖 Powered by *ALTUS AI*"""

            else:
                wa_template = """Saludos cordiales,

*Francisco Valencia*
Managing Partner | Asesor Financiero Senior
🏢 *FV Asesorías e Inversiones*
🤖 Powered by *ALTUS AI*
📱 +56 9 6677 9662
✉️ contacto@fv-inversiones.com
🌐 https://fv-inversiones.com"""

            st.code(wa_template, language="markdown")

        with firm_tab2:
            st.markdown("##### 📧 Firma HTML Profesional para Correo Electrónico (Outlook / Gmail)")
            st.caption("Copia el código HTML o la vista previa para pegarla directamente en la configuración de firma de tu cliente de correo.")

            html_signature = """<table cellpadding="0" cellspacing="0" style="font-family: 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 14px; color: #1e293b; line-height: 1.4;">
  <tr>
    <td style="padding-right: 25px; vertical-align: middle; border-right: 3px solid #d97706;">
      <img src="https://fv-gestion.streamlit.app/app/static/media/src/web/assets/brand/fv_logo_principal.png" alt="FV Asesorias e Inversiones" style="width: 170px; height: auto; display: block;" />
    </td>
    <td style="padding-left: 25px; vertical-align: middle;">
      <div style="font-size: 20px; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; margin-bottom: 2px;">Francisco Valencia</div>
      <div style="font-size: 13px; font-weight: 600; color: #d97706; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">Managing Partner | Asesor Financiero Senior</div>
      
      <div style="font-size: 13px; color: #475569; margin-bottom: 4px;">
        ✉️ <a href="mailto:contacto@fv-inversiones.com" style="color: #0284c7; text-decoration: none; font-weight: 500;">contacto@fv-inversiones.com</a>
      </div>
      <div style="font-size: 13px; color: #475569; margin-bottom: 4px;">
        💬 <a href="https://wa.me/56966779662" style="color: #16a34a; text-decoration: none; font-weight: 500;">+56 9 6677 9662</a>
      </div>
      <div style="font-size: 13px; color: #475569; margin-bottom: 12px;">
        🔗 <a href="https://www.linkedin.com/in/francisco-valencia" style="color: #0284c7; text-decoration: none; font-weight: 500;">Sígueme en LinkedIn</a>
      </div>
      
      <div style="font-size: 11px; font-weight: 600; color: #94a3b8; letter-spacing: 2px; text-transform: uppercase;">
        POWERED BY <span style="color: #d97706; font-weight: 700;">ALTUS AI</span>
      </div>
    </td>
  </tr>
</table>"""

            st.markdown("###### 👁️ Vista Previa de la Firma HTML:")
            st.components.v1.html(html_signature, height=180)
            
            st.markdown("###### 💻 Código HTML para Copiar:")
            st.code(html_signature, language="html")
