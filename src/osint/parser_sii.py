import pdfplumber
import pandas as pd
import io
import re

def parse_sii_carpeta_pdf(file_bytes):
    """
    Parsea la Carpeta Tributaria del SII.
    Extrae la participación en sociedades, rentas declaradas, y propiedades registradas.
    Retorna (df_sociedades, renta_anual, df_propiedades)
    """
    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
        full_text = '\n'.join([p.extract_text() for p in pdf.pages if p.extract_text()])
        lines = full_text.split('\n')
        
        sociedades = []
        propiedades = []
        renta_anual = 0.0
        
        in_sociedades = False
        in_propiedades = False
        
        current_prop = {}
        
        for i, line in enumerate(lines):
            # --- PARSEO DE SOCIEDADES ---
            if "Participación en sociedades vigentes (2)" in line or ("Participaci" in line and "vigentes (2)" in line):
                in_sociedades = True
                clean_line = line.replace("Participación en sociedades vigentes (2)", "").replace("Participacin en sociedades vigentes (2)", "").strip()
                if clean_line:
                    match = re.search(r'(.+?)\s+([\d\.-]+-[kK\d])\s+(\d{2}/\d{2}/\d{4})\s+([\d\.]+%?)\s+([\d\.]+%?)', clean_line)
                    if match:
                        sociedades.append({
                            "RUT Empresa": match.group(2).strip(),
                            "Razón Social": match.group(1).strip(),
                            "Incorporación": match.group(3).strip(),
                            "% Capital": float(match.group(4).replace('%', '').strip()),
                            "% Utilidades": float(match.group(5).replace('%', '').strip()),
                        })
                continue
                
            if in_sociedades:
                if "(1) Informaci" in line or "Propiedades y Bienes" in line:
                    in_sociedades = False
                    
                match = re.search(r'(.+?)\s+([\d\.-]+-[kK\d])\s+(\d{2}/\d{2}/\d{4})\s+([\d\.]+%?)\s+([\d\.]+%?)', line)
                if match:
                    sociedades.append({
                        "RUT Empresa": match.group(2).strip(),
                        "Razón Social": match.group(1).strip(),
                        "Incorporación": match.group(3).strip(),
                        "% Capital": float(match.group(4).replace('%', '').strip()),
                        "% Utilidades": float(match.group(5).replace('%', '').strip()),
                    })
            
            # --- PARSEO DE PROPIEDADES ---
            if "Propiedades y Bienes Raíces Registrados en el SII (3)" in line or "Propiedades y Bienes Ra" in line:
                in_propiedades = True
                continue
                
            if in_propiedades:
                # Las comunas suelen estar en mayusculas, seguidas de un ROL xx-xx
                if re.match(r'^[A-Z\s]+\s+\d{4,5}-\d{5}', line):
                    # Guardamos la anterior si existe y está completa
                    if "ROL" in current_prop and "Avalúo Fiscal (CLP)" in current_prop:
                        propiedades.append(current_prop)
                    
                    parts = line.split()
                    # Encontrar el ROL
                    rol_idx = 0
                    for idx, p in enumerate(parts):
                        if re.match(r'^\d+-\d+$', p):
                            rol_idx = idx
                            break
                    
                    comuna = " ".join(parts[:rol_idx])
                    rol = parts[rol_idx]
                    
                    # El destino suele ser la última palabra
                    destino = parts[-1]
                    direccion = " ".join(parts[rol_idx+1:-1])
                    
                    current_prop = {
                        "Nombre/Alias": "Propiedad SII (Carpeta)",
                        "Comuna": comuna,
                        "ROL": rol,
                        "Dirección": direccion,
                        "Destino": destino
                    }
                    
                # Si estamos procesando una propiedad, buscar la línea con valores numéricos y %
                elif "ROL" in current_prop and "%" in line and "/" in line:
                    # Linea tipo: 172.820.338 - - 385.822 Afecto 11704/5554/2020 100%
                    parts = line.split()
                    try:
                        # Extraer avaluo (primer valor)
                        avaluo_str = parts[0].replace('.', '')
                        if avaluo_str.isdigit():
                            current_prop["Avalúo Fiscal (CLP)"] = float(avaluo_str)
                            
                        # Extraer porcentaje (último valor)
                        pct_str = parts[-1].replace('%', '')
                        current_prop["% de Derecho"] = float(pct_str)
                        
                        # Extraer Fojas/Numero/Año
                        for p in parts:
                            if '/' in p and len(p.split('/')) == 3:
                                fna = p.split('/')
                                current_prop["Fojas"] = fna[0]
                                current_prop["Número"] = fna[1]
                                current_prop["Año"] = fna[2]
                                break
                                
                    except Exception as e:
                        pass
        
        if "ROL" in current_prop and "Avalúo Fiscal (CLP)" in current_prop:
            propiedades.append(current_prop)
                        
        # Renta declarada
        for line in lines:
            if "Total Ingresos Brutos" in line or "Base Imponible" in line:
                parts = line.split()
                try:
                    nums = [float(p.replace('.', '').replace(',', '.')) for p in parts if p.replace('.', '').replace(',', '').isdigit()]
                    if nums:
                        renta_anual = nums[-1]
                except:
                    pass
                    
        return pd.DataFrame(sociedades), renta_anual, pd.DataFrame(propiedades)
        
    except Exception as e:
        print(f"Error parsing SII PDF: {e}")
        return pd.DataFrame(), 0.0, pd.DataFrame()
