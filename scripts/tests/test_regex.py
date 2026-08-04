import re

content_str = "[{'type': 'text', 'text': 'MEMORANDUM ESTRATEGICO'}]"
print("ORIGINAL:", content_str)

c = re.sub(r"^\[\s*\{\s*['\"]type['\"]\s*:\s*['\"]text['\"]\s*,\s*['\"]text['\"]\s*:\s*['\"]", "", content_str)
c = re.sub(r"['\"]\s*\}\s*\]$", "", c)

print("AFTER SUB:", c)
