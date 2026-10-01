import os
from src.utils.excel_kyc_generator import generar_excel_kyc_corporativo
from src.utils.excel_inventory_generator import generar_excel_inventario_mfo

def create_excel_form():
    out_dir = "PRINCIPAL/PRODUCTOS/SEGURO DE VIDA CON AHORRO PREFERENTE"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Formulario_Cliente_DPS.xlsx")
    
    excel_bytes = generar_excel_kyc_corporativo(client_name="Cliente")
    with open(out_file, "wb") as f:
        f.write(excel_bytes)
        
    print(f"Formulario Excel KYC/DPS Corporativo guardado exitosamente en: {out_file}")
    
    # Generar Inventario MFO
    out_file_mfo = os.path.join(out_dir, "Inventario_MFO_Cliente.xlsx")
    excel_mfo_bytes = generar_excel_inventario_mfo(client_name="Cliente")
    with open(out_file_mfo, "wb") as f:
        f.write(excel_mfo_bytes)
        
    print(f"Plantilla Excel Inventario MFO guardada exitosamente en: {out_file_mfo}")

if __name__ == "__main__":
    create_excel_form()
