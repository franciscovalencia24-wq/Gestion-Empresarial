import os, shutil

root_dir = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR"
src_brand = os.path.join(root_dir, "src", "web", "assets", "brand")
dst_brand = os.path.join(root_dir, "assets", "brand")

# Eliminar carpeta dst_brand y copiar exactamente la versión limpia elegida por el usuario
if os.path.exists(dst_brand):
    shutil.rmtree(dst_brand)

shutil.copytree(src_brand, dst_brand)
print("Sincronización completada! Ambos directorios ahora contienen exactamente los mismos archivos:")
for f in os.listdir(dst_brand):
    print(" -", f)
