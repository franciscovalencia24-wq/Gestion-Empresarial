import pandas as pd
import urllib.parse
import os

def generate_forede_excel():
    # Lista inicial de empresas ancla en la Región de Atacama (potenciales expositores FOREDE)
    empresas = [
        "Compañía Minera del Pacífico CMP",
        "Minera Candelaria Lundin Mining",
        "Pucobre",
        "Minera Caserones Lumina Copper",
        "Kinross Chile",
        "Gold Fields Salares Norte",
        "ENAMI",
        "Ferronor",
        "Proyecto NuevaUnión",
        "Fenix Gold",
        "Capstone Copper Santo Domingo",
        "Grupo Minero Carola Coemin",
        "Atacama Kozan",
        "Minera Salar Blanco",
        "Finning CAT Copiapó",
        "Komatsu Copiapó",
        "Epiroc",
        "Sandvik",
        "FLSmidth",
        "Metso",
        "Bailac",
        "Resiter",
        "Empresas Vecchiola",
        "Grupo Gomez Copiapó",
        "Transportes Depetris",
        "Transportes Cruz",
        "Nueva Atacama"
    ]
    
    data = []
    
    for emp in empresas:
        # Búsqueda OSINT en LinkedIn usando Google Dorking
        query = f'site:linkedin.com/in ("Gerente General" OR "General Manager" OR "CEO" OR "Dueño" OR "Gerente de Finanzas") "{emp}" (Copiapó OR Atacama OR Chile)'
        dork_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        # Mensaje propuesto (Plantilla para copiar y pegar)
        mensaje_propuesto = (
            f"Hola, ¿qué tal? Noté que {emp} estará presente en la EXPO FOREDE 2026 este mes de octubre en Copiapó.\n\n"
            f"Desde FV Asesorías (expertos en estructuración patrimonial) también estaremos por la zona participando del evento. "
            f"Me encantaría aprovechar la instancia para tomarnos un café de 15 minutos en el Parque El Pretil o agendar una llamada rápida esa semana para explorar sinergias. ¿Cómo está tu agenda?"
        )
        
        data.append({
            "Empresa (Target)": emp,
            "Cargos a buscar": "Gerente General, CEO, CFO, Dueño",
            "LinkedIn Dork (Clickeable)": dork_url,
            "Nombre del Contacto Encontrado": "",  # Para que el usuario lo llene manualmente
            "Cargo": "",
            "Link Perfil": "",
            "Mensaje a Enviar (Copiar/Pegar)": mensaje_propuesto,
            "Estado del Contacto": "Por Contactar"
        })
        
    df = pd.DataFrame(data)
    
    # Crear carpeta si no existe
    output_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "FOREDE_2026_Prospecting_List.xlsx")
    
    # Guardar en Excel con formato auto-ajustable
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads FOREDE')
        worksheet = writer.sheets['Leads FOREDE']
        
        # Ajustar anchos de columnas
        worksheet.column_dimensions['A'].width = 35
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 30
        worksheet.column_dimensions['E'].width = 25
        worksheet.column_dimensions['F'].width = 15
        worksheet.column_dimensions['G'].width = 100
        worksheet.column_dimensions['H'].width = 20
        
    print(f"Archivo Excel generado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_forede_excel()
