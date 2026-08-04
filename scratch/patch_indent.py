with open('src/web/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('              "Análisis Técnico y Fundamental",', '            "Análisis Técnico y Fundamental",')
text = text.replace('              st.title("🎯 Hub de Análisis de Inversiones")', '            st.title("🎯 Hub de Análisis de Inversiones")')
text = text.replace('              st.markdown("Selecciona qué aspecto del patrimonio deseas evaluar hoy.")', '            st.markdown("Selecciona qué aspecto del patrimonio deseas evaluar hoy.")')

# Also fix the button indentation if it was wrong
text = text.replace('              c1.button("📈 Análisis Técnico y Fundamental"', '            c1.button("📈 Análisis Técnico y Fundamental"')

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Indentation fixed.")
