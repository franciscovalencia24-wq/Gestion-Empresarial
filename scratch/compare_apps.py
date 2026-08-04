import os
import time

app_root = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\app.py"
app_web = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\src\web\app.py"

def file_info(path):
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        size = os.path.getsize(path)
        print(f"File: {path}")
        print(f"  Size: {size} bytes")
        print(f"  Modified: {time.ctime(mtime)}")
    else:
        print(f"File: {path} NOT found")

file_info(app_root)
file_info(app_web)

# Let's count occurrences of some keywords
keywords = ["render_academic_advisor", "render_infoprobidad_ui", "render_industry_insights", "8502", "port"]
for kw in keywords:
    print(f"\nKeyword: '{kw}'")
    for path in [app_root, app_web]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                count = content.count(kw)
                print(f"  In {os.path.basename(path)}: {count} times")
