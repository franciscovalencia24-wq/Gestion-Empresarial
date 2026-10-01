import requests
from bs4 import BeautifulSoup
import re

def get_ipsa_google():
    url = 'https://www.google.com/finance/quote/SP_IPSA:INDEXSANTIAGO'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=10)
    match = re.search(r'data-last-price="([^"]+)"', r.text)
    if match:
        val = float(match.group(1))
        # Format it as Chilean string e.g., "11.290,90"
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return None

print(get_ipsa_google())
