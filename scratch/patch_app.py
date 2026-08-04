import re

with open('src/web/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the sidebar with 4 categories
new_sidebar = '''
    nav = st.sidebar.radio("Navegación Principal", [
        "🏢 1. Gestión de Clientes", 
        "📊 2. Análisis Integral de Activos", 
        "💼 3. Gestión Comercial", 
        "📥 4. Ingesta de Datos"
    ])

    if nav == "🏢 1. Gestión de Clientes":
        from src.web.client_management_ui_new import render_client_management_ui
        render_client_management_ui()

    elif nav == "📊 2. Análisis Integral de Activos":
        from src.web.analysis_hub_ui import render_analysis_hub
        render_analysis_hub()

    elif nav == "💼 3. Gestión Comercial":
        if "sub_nav_comercial" not in st.session_state:
            st.session_state.sub_nav_comercial = "🚀 Motor de Campañas"
        sub_nav = st.sidebar.selectbox("Módulo Comercial", [
            "🚀 Motor de Campañas", 
            "📊 Embudo CRM (Kanban)",
            "🌊 Innovación & Océanos Azules",
            "🧠 Diseñador de Flujos (Playbook)",
            "📱 Generador de Infografías RRSS"
        ], key="sub_nav_comercial")
        
        if sub_nav == "🚀 Motor de Campañas":
            try:
                from src.web.app import render_campaign_launcher
                render_campaign_launcher()
            except ImportError:
                import streamlit as st
                st.info('Módulo en construcción')
        elif sub_nav == "📊 Embudo CRM (Kanban)":
            try:
                from src.web.app import render_crm_kanban
                render_crm_kanban()
            except ImportError:
                import streamlit as st
                st.info('Módulo en construcción')
        elif sub_nav == "🌊 Innovación & Océanos Azules":
            try:
                from src.web.app import render_blue_ocean_ui
                render_blue_ocean_ui()
            except ImportError:
                import streamlit as st
                st.info('Módulo en construcción')
        elif sub_nav == "🧠 Diseñador de Flujos (Playbook)":
            try:
                from src.web.app import render_flujograma
                render_flujograma()
            except ImportError:
                import streamlit as st
                st.info('Módulo en construcción')
        elif sub_nav == "📱 Generador de Infografías RRSS":
            from src.web.infographic_generator_ui import render_infographic_generator_ui
            render_infographic_generator_ui()

    elif nav == "📥 4. Ingesta de Datos":
        try:
            from src.web.app import render_unified_vault
            render_unified_vault()
        except ImportError:
            import streamlit as st
            st.info('Módulo en construcción')

    st.sidebar.markdown("---")
    import datetime
    st.sidebar.markdown(f"v4.0.0 | Metodología Activa | Sincronizado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
'''

content = re.sub(r'nav = st\.sidebar\.radio\(\"Navegaci.*?st\.sidebar\.markdown\(f\"v[^\"]+\"\)', new_sidebar, content, flags=re.DOTALL)

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated app.py successfully')
