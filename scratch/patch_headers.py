import re

with open('src/web/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the gradient divs with simple markdown
def replace_div(match):
    html_content = match.group(1)
    # Extract h1 and p
    h1_match = re.search(r'<h1.*?>(.*?)</h1>', html_content)
    p_match = re.search(r'<p.*?>(.*?)</p>', html_content)
    
    h1_text = h1_match.group(1) if h1_match else ''
    p_text = p_match.group(1) if p_match else ''
    
    return f'st.title("{h1_text}")\n              st.markdown("{p_text}")'

text = re.sub(r'st\.markdown\(\"\"\"\s*<div style=\'background: linear-gradient.*?(Hub de An.*?)</div>\s*\"\"\", unsafe_allow_html=True\)', replace_div, text, flags=re.DOTALL)
text = re.sub(r'st\.markdown\(\"\"\"\s*<div style=\'background: linear-gradient.*?(Simuladores Cuant.*?)</div>\s*\"\"\", unsafe_allow_html=True\)', replace_div, text, flags=re.DOTALL)

with open('src/web/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.py headers fixed safely!')
