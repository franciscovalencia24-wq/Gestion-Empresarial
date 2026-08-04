import os
import re

root_dir = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"

def replace_in_file(file_path, replacements):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    new_content = content
    for old_val, new_val in replacements.items():
        new_content = new_content.replace(old_val, new_val)
        
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Actualizado: {os.path.relpath(file_path, root_dir)}")

# 1. Actualización en generadores de PDF y servicios
replacements = {
    # Reemplazar rutas antiguas a NUEVO LOGO FV / Logo_FV_Principal por la nueva carpeta brand/
    'os.path.join(root_dir, "assets", "NUEVO LOGO FV.svg")': 'os.path.join(root_dir, "assets", "brand", "fv_logo_vector_principal.svg")',
    'os.path.join(root_dir, "src", "web", "assets", "NUEVO LOGO FV.png")': 'os.path.join(root_dir, "assets", "brand", "fv_logo_principal_light.png")',
    'os.path.join(root_dir, "assets", "Logo_FV_Principal.png")': 'os.path.join(root_dir, "assets", "brand", "fv_logo_principal_light.png")',
    'os.path.join(root_assets_dir, "Logo_FV_Negativo.png")': 'os.path.join(root_dir, "assets", "brand", "fv_logo_blanco_negativo.png")',
    'assets/Logo_FV_Negativo.png': 'assets/brand/fv_logo_blanco_negativo.png',
    'assets/Logo_FV_Negativo.svg': 'assets/brand/fv_logo_vector_negativo.svg',
    'src/web/assets/NUEVO LOGO FV.png': 'assets/brand/fv_logo_principal_light.png',
    'src/web/assets/ALTUS_AI_LOGO.png': 'assets/brand/altus_ai_logo_principal.png',
    'ALTUS_AI_LOGO_BORDES_SUAVIZADOS.png': 'assets/brand/altus_ai_logo_principal.png',
    'Logo_ALTUS AI_Principal_Fondo oscuro.svg': 'brand/altus_ai_logo_dark.svg',
    'Logo_ALTUS AI_Principal.svg': 'brand/altus_ai_logo_principal.svg'
}

# Archivos a procesar
target_files = [
    os.path.join(root_dir, "src", "reporting", "pdf_engine.py"),
    os.path.join(root_dir, "src", "utils", "pdf_generator_analysis.py"),
    os.path.join(root_dir, "src", "utils", "pdf_generator_apv.py"),
    os.path.join(root_dir, "src", "utils", "pdf_generator_reliquidacion.py"),
    os.path.join(root_dir, "src", "utils", "pdf_generator_macro.py"),
    os.path.join(root_dir, "src", "utils", "simulators", "board_simulator.py"),
    os.path.join(root_dir, "generador_informes.py"),
    os.path.join(root_dir, "src", "reporting", "credito_vs_inversion.py"),
    os.path.join(root_dir, "src", "osint", "market_data_engine.py"),
    os.path.join(root_dir, "build_infografia.py"),
    os.path.join(root_dir, "build_reforma_2026_infographic.py"),
    os.path.join(root_dir, "src", "web", "app.py"),
    os.path.join(root_dir, "propuesta.html"),
    os.path.join(root_dir, "pitch_interno.html"),
    os.path.join(root_dir, "anuncio_moderno.html"),
    os.path.join(root_dir, "anuncio_revista_altus.html"),
    os.path.join(root_dir, "firma_correo_altus.html"),
    os.path.join(root_dir, "informe_arquitectura_tecnica.html"),
    os.path.join(root_dir, "informe_ia.html"),
    os.path.join(root_dir, "PRINCIPAL", "PRODUCTOS", "SEGURO DE VIDA CON AHORRO PREFERENTE", "infografia_seguro.html"),
    os.path.join(root_dir, "PRINCIPAL", "PRODUCTOS", "SEGURO DE VIDA CON AHORRO PREFERENTE", "generador_producto_seguro.html")
]

for tf in target_files:
    replace_in_file(tf, replacements)

print("\nSincronización completa de rutas de marca.")
