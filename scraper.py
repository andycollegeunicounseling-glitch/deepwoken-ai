import requests
import json
import os
import sys

os.makedirs('data', exist_ok=True)

# Disguise the request to look exactly like a normal Chrome browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

print("Fetching pages from Deepwoken Fandom...")
url = "https://deepwoken.fandom.com/api.php"

params = {
    "action": "query",
    "format": "json",
    "list": "allpages",
    "aplimit": "10" # Keeping it low to test
}

# Test the connection
response = requests.get(url, headers=headers, params=params)
print(f"Server Status Code: {response.status_code}")

# Check if Cloudflare blocked us
if response.status_code != 200:
    print("ERROR: Fandom blocked the request!")
    sys.exit(1)

data = response.json()
print("Successfully connected!")

wiki_data = []

# Process the pages
if 'query' in data and 'allpages' in data['query']:
    pages = data['query']['allpages']
    
    for page in pages:
        title = page['title']
        print(f"Downloading: {title}")
        
        content_params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True
        }
        res = requests.get(url, headers=headers, params=content_params).json()
        
        pages_dict = res.get('query', {}).get('pages', {})
        for page_id, page_info in pages_dict.items():
            text = page_info.get('extract', '')
            if text and len(text.strip()) > 0:
                wiki_data.append({"title": title, "content": text})

# Save output
with open('data/deepwoken_wiki.json', 'w', encoding='utf-8') as f:
    json.dump(wiki_data, f, indent=4)

print(f"Done! Saved {len(wiki_data)} pages.")
