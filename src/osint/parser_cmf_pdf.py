import pdfplumber
import pandas as pd
import io
import re

def parse_cmf_insurance_pdf(file_path_or_bytes):
    """
    Parsea un certificado de 'Conoce Tu Seguro' (CMF) extraído en formato PDF
    y devuelve un DataFrame de pandas con las pólizas consolidadas y nuevos campos.
    """
    try:
        if isinstance(file_path_or_bytes, bytes):
            pdf = pdfplumber.open(io.BytesIO(file_path_or_bytes))
        else:
            pdf = pdfplumber.open(file_path_or_bytes)
            
        full_text = '\n'.join([p.extract_text() for p in pdf.pages if p.extract_text()])
        
        # Eliminar saltos de línea molestos que cortan "Número o código del \n contrato"
        full_text = re.sub(r'Número o código del\s*\n\s*contrato', 'Número o código del contrato', full_text)
        
        sections = full_text.split('Detalle Póliza ')
        
        result_list = []
        
        for sec in sections[1:]: # El primer elemento es antes del primer detalle
            lines = [line.strip() for line in sec.split('\n') if line.strip()]
            if not lines: continue
            
            # El primer token de la primera línea suele ser el número de la póliza (del encabezado del detalle)
            pol_num_header = lines[0].split()[0]
            
            aseguradora = ""
            asegurado = ""
            contratante = ""
            numero_contrato = pol_num_header
            estado = "VIGENTE"
            colectiva_individual = ""
            coberturas = []
            
            in_coberturas = False
            for i, line in enumerate(lines):
                if line.startswith("Aseguradora :"):
                    aseguradora = line.split(":", 1)[1].strip()
                elif line.startswith("Asegurado :"):
                    asegurado = line.split(":", 1)[1].strip()
                elif line.startswith("Contratante :"):
                    contratante = line.split(":", 1)[1].strip()
                elif line.startswith("Número o código del contrato :"):
                    numero_contrato = line.split(":", 1)[1].strip()
                elif line.startswith("Estado :"):
                    estado = line.split(":", 1)[1].strip()
                elif line.startswith("Colectiva/Individual :"):
                    colectiva_individual = line.split(":", 1)[1].strip()
                elif line.startswith("Coberturas:"):
                    in_coberturas = True
                    continue
                elif line.startswith("COMPAÑÍAS QUE NO RESPONDIERON"):
                    in_coberturas = False
                    break
                    
                if in_coberturas:
                    # Filter out page headers/footers that might interrupt coverages
                    if "Fecha de emisi" in line or "Página" in line or "Conoce Tu Seguro" in line:
                        continue
                    coberturas.append(line)
                    
            coberturas_str = "\n".join(coberturas).strip()
            
            # Limpiar posibles errores de la CMF en el nombre de la aseguradora
            aseguradora = aseguradora.replace("\ufffd", "Ñ")
            
            # Inferir Tipo de Bien Asegurado
            tipo_bien = inferir_tipo_bien(coberturas_str)
            
            result_list.append({
                "compania": aseguradora,
                "asegurado": asegurado,
                "contratante": contratante,
                "numero_poliza": numero_contrato,
                "estado": estado,
                "colectivo_individual": colectiva_individual,
                "coberturas": coberturas_str,
                "tipo_seguro": tipo_bien # Utilizamos 'tipo_seguro' para esto en la UI antigua, pero lo renombraremos
            })
            
        # Extraer COMPAÑÍAS QUE NO RESPONDIERON LA CONSULTA
        no_responden = []
        try:
            last_page_text = pdf.pages[-1].extract_text()
            if "COMPA" in last_page_text and "NO RESPONDIERON" in last_page_text:
                lines = last_page_text.split("\n")
                in_no_responden = False
                for line in lines:
                    if "NO RESPONDIERON" in line:
                        in_no_responden = True
                        continue
                    if in_no_responden:
                        if line.strip() == "" or line.startswith("-") or "La información es proporcionada" in line:
                            break
                        cia = line.replace("•", "").strip()
                        if cia:
                            no_responden.append(cia)
        except Exception as e:
            pass
            
        return pd.DataFrame(result_list), no_responden
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return pd.DataFrame(), []

def inferir_tipo_bien(coberturas_str):
    """
    Infiere el tipo de bien asegurado basado en las palabras clave de las coberturas.
    """
    text = coberturas_str.lower()
    if "vehículo" in text or "auto" in text or "responsabilidad civil por daños causados por el vehículo" in text:
        return "Vehículo"
    elif "hipotecario" in text or "incendio" in text or "sismo" in text or "terremoto" in text:
        return "Inmueble / Hipotecario"
    elif "salud" in text or "catastrófico" in text or "dental" in text or "enfermedad" in text:
        return "Salud"
    elif "vida" in text or "fallecimiento" in text or "accidentes personales" in text:
        return "Vida / Accidentes"
    elif "consumo" in text or "tarjeta" in text or "fraude" in text:
        return "Crédito Consumo / Tarjeta"
    else:
        return "Otros / Mixto"
