import difflib

app_root = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\app.py"
app_web = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\app.py"

with open(app_root, "r", encoding="utf-8", errors="ignore") as f:
    root_lines = f.readlines()

with open(app_web, "r", encoding="utf-8", errors="ignore") as f:
    web_lines = f.readlines()

print(f"Root: {len(root_lines)} lines")
print(f"Web: {len(web_lines)} lines")

# Show lines that are in root but not in web, or vice versa
diff = list(difflib.unified_diff(root_lines, web_lines, fromfile="root_app.py", tofile="web_app.py", n=0))
print(f"Total diff lines: {len(diff)}")
# Print first 20 diff entries
for line in diff[:30]:
    print(line.strip())
