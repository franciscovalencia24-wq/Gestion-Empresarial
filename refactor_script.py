import re

with open("src/web/client_management_ui_new.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

tab2_idx = -1
for i, line in enumerate(lines):
    if line.startswith("    with tab2:"):
        tab2_idx = i
        break

if tab2_idx != -1:
    # Everything before tab2_idx goes into a new render_client_management_ui
    # Actually, the entire file has a def render_client_management_ui(): at the top.
    # We need to find where render_client_management_ui ends. Since it's the only top-level function, it ends at EOF.
    
    top_part = lines[:tab2_idx]
    
    # Let's insert the render_client_profile(is_b2b=False) call in tab2
    new_tab2_call = [
        "    with tab2:\n",
        "        render_client_profile(is_b2b=False)\n\n",
        "def render_client_profile(is_b2b=False):\n"
    ]
    
    # We need to dedent the lines from tab2_idx+1 to EOF by 4 spaces.
    # Wait, the lines inside "with tab2:" are indented with 8 spaces.
    # If we put them inside a function, they should be indented with 4 spaces.
    
    body_lines = lines[tab2_idx+1:]
    dedented_lines = []
    for line in body_lines:
        if line.startswith("    "):
            dedented_lines.append(line[4:])
        else:
            dedented_lines.append(line)
            
    final_lines = top_part + new_tab2_call + dedented_lines
    
    with open("src/web/client_management_ui_new.py", "w", encoding="utf-8") as f:
        f.writelines(final_lines)
    print("Refactored successfully")
else:
    print("Could not find tab2")
