import urllib.request
import re

url = "https://unsplash.com/s/photos/stock-market"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    ids = re.findall(r'images\.unsplash\.com/photo-([a-zA-Z0-9\-]+)\?', html)
    unique_ids = list(set(ids))
    print(f"Encontrados: {len(unique_ids)}")
    for uid in unique_ids[:20]:
        print(f"https://images.unsplash.com/photo-{uid}?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80")
except Exception as e:
    print(e)
