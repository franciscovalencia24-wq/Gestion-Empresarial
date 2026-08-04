import os
import shutil

root_dir = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"

brand_dir_web = os.path.join(root_dir, "src", "web", "assets", "brand")
brand_dir_root = os.path.join(root_dir, "assets", "brand")

# Definir la lista única y canónica de logos con nombres limpios y representativos
canonical_logos = {
    # LOGOS DE FV ASESORÍAS E INVERSIONES
    "fv_logo_principal.png": "Logo_FV_Principal.png",              # PNG claro oficial
    "fv_logo_principal.svg": "Logo_FV_Principal.svg",              # SVG claro oficial
    "fv_logo_negativo.png": "Logo_FV_Negativo.png",                # PNG blanco/negativo para fondos oscuros
    "fv_logo_negativo.svg": "Logo_FV_Negativo.svg",                # SVG blanco/negativo para fondos oscuros
    "fv_icono_isotipo.svg": "Icono_FV_Principal.svg",              # Isotipo FV solo símbolo (SVG)
    "fv_icono_isotipo_amplio.png": "Icono_FV_Principal_amplio.png",# Isotipo FV ampliado (PNG)
    "fv_monograma.jpg": "fv_isotype_monogram.jpg",                 # Monograma solo letra FV (JPG)
    "fv_emblema_3d_metalico.png": "LOGO VECTORIZADO (2).png",       # Emblema 3D metálico en PNG
    "fv_emblema_3d_metalico.svg": "LOGO VECTORIZADO (2).svg",       # Emblema 3D metálico en SVG

    # LOGOS DE ALTUS AI (WEALTHTECH)
    "altus_ai_logo_principal.png": "Logo_ALTUS AI_Principal.png",          # PNG claro oficial
    "altus_ai_logo_principal.svg": "Logo_ALTUS AI_Principal.svg",          # SVG claro oficial
    "altus_ai_logo_dark.png": "Logo_ALTUS AI_Principal_Fondo oscuro.png",  # PNG fondo oscuro
    "altus_ai_logo_dark.svg": "Logo_ALTUS AI_Principal_Fondo oscuro.svg",  # SVG fondo oscuro
    "altus_ai_logo_negativo.png": "Logo_ALTUS AI_Negativo.png",            # PNG blanco puro
    "altus_ai_logo_negativo.svg": "Logo_ALTUS AI_Negativo.svg",            # SVG blanco puro
}

# Aliases de compatibilidad para código existente
aliases = {
    "fv_logo_principal_light.png": "fv_logo_principal.png",
    "fv_logo_vector_principal.svg": "fv_logo_principal.svg",
    "fv_logo_blanco_negativo.png": "fv_logo_negativo.png",
    "fv_logo_vector_negativo.svg": "fv_logo_negativo.svg",
    "fv_emblem_3d_metallic.png": "fv_emblema_3d_metalico.png",
    "fv_emblem_3d_metallic.svg": "fv_emblema_3d_metalico.svg",
}

print("=== INICIANDO LIMPIEZA Y DEPURACIÓN DE MARCA ===")

# Crear o limpiar directorio limpio
temp_dir = os.path.join(root_dir, "temp_brand_clean")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)

# Copiar archivos canónicos desde assets/ o src/web/assets/brand/
for target_name, src_name in canonical_logos.items():
    found_path = None
    possible_paths = [
        os.path.join(brand_dir_web, src_name),
        os.path.join(root_dir, "assets", src_name),
        os.path.join(brand_dir_web, target_name),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if found_path:
        dest_path = os.path.join(temp_dir, target_name)
        shutil.copy2(found_path, dest_path)
        print(f"[OK] {target_name} <- {os.path.basename(found_path)}")
    else:
        print(f"[MISSING] No se encontró {src_name}")

# Crear enlaces/copias de compatibilidad para que el código existente no falle
for alias_name, canonical_target in aliases.items():
    src_canonical = os.path.join(temp_dir, canonical_target)
    dest_alias = os.path.join(temp_dir, alias_name)
    if os.path.exists(src_canonical):
        shutil.copy2(src_canonical, dest_alias)
        print(f"[ALIAS] {alias_name} -> {canonical_target}")

# Ahora vaciar y actualizar ambas carpetas de marca
for target_brand in [brand_dir_web, brand_dir_root]:
    os.makedirs(target_brand, exist_ok=True)
    # Limpiar contenido anterior
    for item in os.listdir(target_brand):
        item_path = os.path.join(target_brand, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
    # Copiar contenido limpio
    for item in os.listdir(temp_dir):
        shutil.copy2(os.path.join(temp_dir, item), os.path.join(target_brand, item))
    print(f"\nDirectorio {os.path.relpath(target_brand, root_dir)} actualizado con {len(os.listdir(target_brand))} archivos limpios.")

# Borrar directorio temporal
shutil.rmtree(temp_dir)
print("\n¡Depuración completada exitosamente!")
