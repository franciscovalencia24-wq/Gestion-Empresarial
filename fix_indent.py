with open('src/intelligence/market_analyst.py', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for i, l in enumerate(lines):
    if 70 <= i <= 170 and l.strip() and not l.startswith('if __name__'):
        out.append('    ' + l)
    else:
        out.append(l)

with open('src/intelligence/market_analyst.py', 'w', encoding='utf-8') as f:
    f.writelines(out)
