with open(r'c:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\client_management_ui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'Seguros' in line and 'expander' in line:
        print(f"Line {i+1}: {line.strip().encode('ascii', 'ignore').decode('ascii')}")
