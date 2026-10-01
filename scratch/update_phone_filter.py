import re

file_path = r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# For discarded mode
pattern1 = r"SELECT \* FROM prospects WHERE \(status_contacto LIKE 'Descartado%' OR status_contacto = 'No Contactar' OR telefono LIKE '%ERROR%'\)"
replacement1 = r"SELECT * FROM prospects WHERE (status_contacto LIKE 'Descartado%' OR status_contacto = 'No Contactar' OR telefono LIKE '%ERROR%' OR telefono = 'No encontrado' OR LENGTH(telefono) < 8)"
content = content.replace(pattern1, replacement1)

# For prospeccion mode
pattern2 = r"AND telefono != 'None' AND nombre != 'None' AND telefono NOT LIKE '%ERROR%'"
replacement2 = r"AND telefono != 'None' AND nombre != 'None' AND telefono NOT LIKE '%ERROR%' AND telefono != 'No encontrado' AND LENGTH(telefono) >= 8"
content = content.replace(pattern2, replacement2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
