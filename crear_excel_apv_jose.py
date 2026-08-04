import os
from src.utils.excel_kyc_generator import generar_excel_apv_reliquidacion

def build_excel_apv_jose():
    out_dir = "PRINCIPAL/PRODUCTOS/APV"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Formulario_APV_Reliquidacion_Jose_Gonzalez_Daza.xlsx")
    
    excel_bytes = generar_excel_apv_reliquidacion(client_name="José González Daza")
    with open(out_file, "wb") as f:
        f.write(excel_bytes)
        
    print(f"Formulario Excel APV & Reliquidación para José González Daza guardado exitosamente en: {out_file}")

if __name__ == "__main__":
    build_excel_apv_jose()
