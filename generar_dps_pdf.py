import fitz
import openpyxl
import sys
import re

def clean_name(text):
    return re.sub(r'[^a-zA-Z0-9_]', '', text)

def add_text_field(page, text_to_find, field_value, offset_x=0, offset_y=1, width=150, height=13, font_size=8, color=(0,0,1), occurrence=0):
    rects = page.search_for(text_to_find)
    if rects and len(rects) > occurrence:
        rect = rects[occurrence]
        # La caja blanca está generalmente debajo del texto, desde rect.y1 hacia abajo.
        w_rect = fitz.Rect(rect.x0 + offset_x, rect.y1 + offset_y, rect.x0 + offset_x + width, rect.y1 + offset_y + height)
        
        w = fitz.Widget()
        w.rect = w_rect
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.field_name = f"text_{clean_name(text_to_find)}_{occurrence}"
        w.field_value = str(field_value).upper()
        w.text_fontsize = font_size
        w.text_color = color
        page.add_widget(w)
        return True
    return False

def find_word_rects(page, target_word):
    """Busca una palabra exacta (case-sensitive)."""
    words = page.get_text("words")
    rects = []
    for w in words:
        if w[4] == target_word:
            rects.append(fitz.Rect(w[0], w[1], w[2], w[3]))
    return rects

def find_closest_rect(q_rect, ans_rects, max_dist_y=35):
    best_rect = None
    min_dist = float('inf')
    for r in ans_rects:
        if r.y0 < q_rect.y0 - 5:
            continue
        if r.y0 > q_rect.y0 + max_dist_y:
            continue
            
        dist = (r.x0 - q_rect.x0)**2 + (r.y0 - q_rect.y0)**2
        if dist < min_dist:
            min_dist = dist
            best_rect = r
    return best_rect

def add_checkbox_field(page, question_text, answer):
    q_rects = page.search_for(question_text)
    if not q_rects: return False
    q_rect = q_rects[0]
    
    is_yes = str(answer).strip().lower().startswith("s")
    target_text = "Si" if is_yes else "No"
    
    ans_rects = find_word_rects(page, target_text)
    best_rect = find_closest_rect(q_rect, ans_rects)
    
    if best_rect:
        # Movemos la caja un poco más a la derecha (x1 + 6) y un poco abajo (y0 + 1) para centrar la X en el cuadradito
        w_rect = fitz.Rect(best_rect.x1 + 6, best_rect.y0 + 1, best_rect.x1 + 16, best_rect.y1 + 5)
        
        w = fitz.Widget()
        w.rect = w_rect
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.field_name = f"check_{clean_name(question_text)}"
        w.field_value = "X"
        w.text_fontsize = 10
        w.text_color = (0,0,1)
        page.add_widget(w)
        return True
    return False

def generar_pdf(excel_file, pdf_in, pdf_out):
    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        return

    ws1 = wb["1. Datos Personales"]
    ws2 = wb["2. Hábitos y Actividades"]
    ws3 = wb["3. Antecedentes Médicos"]
    
    doc = fitz.open(pdf_in)
    
    # --- PÁGINA 1 ---
    page1 = doc[0]
    page1.clean_contents() # Limpieza por si acaso
    
    # Datos Personales (cajas debajo del texto: offset_y=4, height=9)
    add_text_field(page1, "Apellido Paterno", ws1['B4'].value or "", width=170, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Apellido Materno", ws1['B5'].value or "", width=170, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Nombres", ws1['B3'].value or "", width=200, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "RUT", ws1['B6'].value or "", width=150, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Fecha de Nacimiento", ws1['B7'].value or "", width=150, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Profesión u Oﬁ cio", ws1['B8'].value or "", width=200, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Nombre del Empleador", ws1['B9'].value or "", width=160, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Giro de la Empresa", ws1['B10'].value or "", width=140, height=9, font_size=0, offset_y=4)
    add_text_field(page1, "Especiﬁ que tipo de actividad", ws1['B11'].value or "", width=140, height=9, font_size=0, offset_y=4)
    
    # Lugar de trabajo (checkbox Oficina / Terreno)
    lugar = str(ws1['B12'].value or "").lower()
    if "oficina" in lugar:
        rects = find_word_rects(page1, "Oficina")
        if rects:
            w_rect = fitz.Rect(rects[0].x0 - 15, rects[0].y0, rects[0].x0 - 5, rects[0].y1 + 4)
            w = fitz.Widget()
            w.rect = w_rect
            w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            w.field_name = "check_oficina"
            w.field_value = "X"
            w.text_color = (0,0,1)
            page1.add_widget(w)
    elif "terreno" in lugar:
        rects = find_word_rects(page1, "Terreno")
        if rects:
            w_rect = fitz.Rect(rects[0].x0 - 15, rects[0].y0, rects[0].x0 - 5, rects[0].y1 + 4)
            w = fitz.Widget()
            w.rect = w_rect
            w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            w.field_name = "check_terreno"
            w.field_value = "X"
            w.text_color = (0,0,1)
            page1.add_widget(w)
            
    # Misma línea: offset_y=-9, height=9
    add_text_field(page1, "Lugar donde trabaja", ws1['B13'].value or "", offset_x=130, width=120, height=9, font_size=0, offset_y=-9)

    # Hábitos y Actividades
    add_checkbox_field(page1, "¿Tiene algún Seguro de Vida", ws2['B4'].value or "No")
    add_text_field(page1, "Indique Compañía", ws2['C4'].value or "", offset_x=85, offset_y=-9, width=100, height=9, font_size=0)

    add_checkbox_field(page1, "¿Practica algún Deporte", ws2['B5'].value or "No")
    add_text_field(page1, "Detalle", ws2['C5'].value or "", offset_x=40, offset_y=-9, width=350, height=9, font_size=0, occurrence=0)

    add_checkbox_field(page1, "¿Realiza alguna actividad", ws2['B6'].value or "No")
    add_text_field(page1, "Detalle", ws2['C6'].value or "", offset_x=40, offset_y=-9, width=350, height=9, font_size=0, occurrence=1)
    
    add_checkbox_field(page1, "¿Ha fumado en los últimos", ws2['B7'].value or "No")
    add_text_field(page1, "¿Cuánto fuma diariamente?", ws2['C7'].value or "", offset_x=140, offset_y=-9, width=80, height=9, font_size=0)

    add_checkbox_field(page1, "¿Ingiere bebidas alcohólicas?", ws2['B8'].value or "No")
    add_text_field(page1, "Indique tipo de bebida", ws2['C8'].value or "", offset_x=120, offset_y=-9, width=120, height=9, font_size=0)

    # Vuelos y moto
    vuelos = str(ws2['B11'].value or "No")
    add_checkbox_field(page1, "¿Realiza vuelos de línea comercial", vuelos)
    add_text_field(page1, "Especiﬁque", ws2['C11'].value or "", offset_x=60, offset_y=-9, width=150, height=9, font_size=0)

    vuelos_no = str(ws2['B12'].value or "No")
    add_checkbox_field(page1, "¿Realiza vuelos de línea no comercial", vuelos_no)
    add_text_field(page1, "Detalle", ws2['C12'].value or "", offset_x=40, offset_y=-9, width=200, height=9, font_size=0, occurrence=4)

    moto = str(ws2['B13'].value or "No")
    add_checkbox_field(page1, "¿Utiliza moto?", moto)
    add_text_field(page1, "Indique Cilindrada", ws2['C13'].value or "", offset_x=90, offset_y=-9, width=50, height=9, font_size=0)
    add_text_field(page1, "Indique hrs./mes", ws2['C14'].value or "", offset_x=90, offset_y=-9, width=50, height=9, font_size=0)

    # --- PÁGINA 2 ---
    page2 = doc[1]
    page2.clean_contents()
    
    # Medidas
    # Ajuste offset_y a valores negativos porque la caja suele estar al lado
    add_text_field(page2, "Estatura", ws3['B4'].value or "", offset_x=50, offset_y=-9, width=50, height=9, font_size=0)
    add_text_field(page2, "Peso", ws3['B5'].value or "", offset_x=30, offset_y=-9, width=50, height=9, font_size=0)
    
    add_checkbox_field(page2, "variación de más de 5 kg", ws3['B6'].value or "No")
    
    # Presión Arterial
    q_presion = page2.search_for("Su presión arterial es:")
    if q_presion:
        q_rect = q_presion[0]
        presion = str(ws3['B7'].value or "Normal").lower()
        if "alta" in presion:
            ans_rects = find_word_rects(page2, "Alta")
        elif "baja" in presion:
            ans_rects = find_word_rects(page2, "Baja")
        else:
            ans_rects = find_word_rects(page2, "Normal")
            
        best_rect = find_closest_rect(q_rect, ans_rects)
        if best_rect:
            w_rect = fitz.Rect(best_rect.x1 + 3, best_rect.y0, best_rect.x1 + 13, best_rect.y1 + 4)
            w = fitz.Widget()
            w.rect = w_rect
            w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            w.field_name = "check_presion"
            w.field_value = "X"
            w.text_color = (0,0,1)
            page2.add_widget(w)

    # Exámenes
    add_checkbox_field(page2, "Sangre", ws3['B11'].value or "No")
    add_checkbox_field(page2, "Orina", ws3['B12'].value or "No")
    add_checkbox_field(page2, "Electrocardiograma", ws3['B13'].value or "No")
    add_checkbox_field(page2, "Rayos, RNM, TAC", ws3['B14'].value or "No")
    add_checkbox_field(page2, "Otro (Endoscopía", ws3['B15'].value or "No")

    # Cuestionario 5. a-n
    add_checkbox_field(page2, "anormalidad, deformación", ws3['B20'].value or "No") # 5a
    add_checkbox_field(page2, "recibido usted alguna indemnización", ws3['B20'].value or "No") # 5b
    add_checkbox_field(page2, "superior a 1 mes", ws3['B20'].value or "No") # 5c
    add_checkbox_field(page2, "Ha sido hospitalizado?", ws3['B20'].value or "No") # 5d
    add_checkbox_field(page2, "sometido a intervención quirúrgica", ws3['B20'].value or "No") # 5e
    add_checkbox_field(page2, "consultado médico en los últimos cinco años", ws3['B22'].value or "No") # 5i
    add_checkbox_field(page2, "indicación médica de algún tratamiento", ws3['B21'].value or "No") # 5n
    
    # --- PÁGINA 3 ---
    page3 = doc[2]
    page3.clean_contents()
    # Cuestionario 6
    add_checkbox_field(page3, "Vértigos, convulsiones", ws3['B26'].value or "No")
    add_checkbox_field(page3, "Asma, enﬁ sema", ws3['B24'].value or "No")
    add_checkbox_field(page3, "Ulcera del estómago", ws3['B25'].value or "No")
    add_checkbox_field(page3, "Nefritis, nefrosis", ws3['B23'].value or "No")
    add_checkbox_field(page3, "Gota, artritis", ws3['B29'].value or "No")
    add_checkbox_field(page3, "Bocio, hipertiroidismo", ws3['B27'].value or "No")
    add_checkbox_field(page3, "cáncer, patolo", ws3['B28'].value or "No")

    doc.save(pdf_out)
    print(f"PDF generado exitosamente en: {pdf_out}")

if __name__ == "__main__":
    excel_file = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\Formulario_Cliente_DPS_test.xlsx"
    pdf_in = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\Declaración Personal de Salud (Extendida) (1).pdf"
    pdf_out = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\PRINCIPAL\PRODUCTOS\SEGURO DE VIDA CON AHORRO PREFERENTE\DPS_Interactivo_Test_v5.pdf"
    
    generar_pdf(excel_file, pdf_in, pdf_out)
