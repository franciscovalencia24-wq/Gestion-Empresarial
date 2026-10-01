import requests
import re
import json

def get_images(query):
    url = f"https://unsplash.com/s/photos/{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    links = re.findall(r'(https://images\.unsplash\.com/photo-[a-zA-Z0-9\-]+)\?', r.text)
    # Deduplicate and keep format
    unique = list(set(links))
    return [f"{img}?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80" for img in unique[:30]]

results = {
    "bullish": get_images("stock-market-up"),
    "bearish": get_images("financial-crisis"),
    "neutral": get_images("corporate-finance")
}
print(json.dumps({k: len(v) for k, v in results.items()}))
with open("scratch/unsplash_cache.json", "w") as f:
    json.dump(results, f, indent=4)
