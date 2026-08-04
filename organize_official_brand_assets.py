import os
import shutil

root_dir = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"

# Carpetas de marca destinadas
brand_dir_1 = os.path.join(root_dir, "assets", "brand")
brand_dir_2 = os.path.join(root_dir, "src", "web", "assets", "brand")

os.makedirs(brand_dir_1, exist_ok=True)
os.makedirs(brand_dir_2, exist_ok=True)

# Mapeo de archivos de origen a nombres limpios estandarizados
files_map = {
    # Logos de FV Asesorías e Inversiones
    "NUEVO_LOGO_FV_BLANCO_PERFECTO.png": "fv_logo_principal_hd.png",
    "LOGO VECTORIZADO (2).png": "fv_emblem_3d_metallic.png",
    "LOGO VECTORIZADO (2).svg": "fv_emblem_3d_metallic.svg",
    "NUEVO_LOGO_FV_BLANCO.png": "fv_logo_blanco_negativo.png",
    "NUEVO LOGO SOLO LETRA FV.jpg": "fv_isotype_monogram.jpg",
    "assets/Logo_FV_Principal.svg": "fv_logo_vector_principal.svg",
    "assets/Logo_FV_Negativo.svg": "fv_logo_vector_negativo.svg",
    
    # Logos de Altus AI
    "ALTUS_AI_LOGO_BORDES_SUAVIZADOS.png": "altus_ai_logo_principal.png",
    "ALTUS_AI_LOGO_TRANSPARENTE.png": "altus_ai_logo_transparent.png",
    "altus_logo_minimalist_1780936005587.png": "altus_ai_isotype_minimalist.png",
    "assets/Logo_ALTUS AI_Principal.svg": "altus_ai_logo_principal.svg",
    "assets/Logo_ALTUS AI_Principal_Fondo oscuro.svg": "altus_ai_logo_dark.svg",
    "assets/Logo_ALTUS AI_Negativo.svg": "altus_ai_logo_negativo.svg"
}

copied_files = []

for src_rel, target_filename in files_map.items():
    src_path = os.path.join(root_dir, src_rel)
    if os.path.exists(src_path):
        target_path_1 = os.path.join(brand_dir_1, target_filename)
        target_path_2 = os.path.join(brand_dir_2, target_filename)
        shutil.copy2(src_path, target_path_1)
        shutil.copy2(src_path, target_path_2)
        copied_files.append(target_filename)
        print(f"Copiado: {target_filename}")
    else:
        print(f"Advertencia: No se encontró {src_rel}")

print(f"\nTotal archivos organizados en la carpeta brand/: {len(copied_files)}")
