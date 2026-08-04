import os
from src.utils.excel_kyc_generator import generar_excel_kyc_corporativo

def create_excel_form():
    out_dir = "PRINCIPAL/PRODUCTOS/SEGURO DE VIDA CON AHORRO PREFERENTE"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Formulario_Cliente_DPS.xlsx")
    
    excel_bytes = generar_excel_kyc_corporativo(client_name="Cliente")
    with open(out_file, "wb") as f:
        f.write(excel_bytes)
        
    print(f"Formulario Excel KYC/DPS Corporativo guardado exitosamente en: {out_file}")

if __name__ == "__main__":
    create_excel_form()
