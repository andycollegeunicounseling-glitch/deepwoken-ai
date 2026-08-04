import requests
import json
import os
import sys

os.makedirs('data', exist_ok=True)

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
    "aplimit": "500" # Max allowed by MediaWiki for regular users
}

response = requests.get(url, headers=headers, params=params)
if response.status_code != 200:
    print("ERROR: Fandom blocked the request!")
    sys.exit(1)

data = response.json()
wiki_data = []

if 'query' in data and 'allpages' in data['query']:
    pages = data['query']['allpages']
    print(f"Found {len(pages)} pages to download. This might take a minute...")
    
    for page in pages:
        title = page['title']
        
        content_params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main"
        }
        res = requests.get(url, headers=headers, params=content_params).json()
        
        pages_dict = res.get('query', {}).get('pages', {})
        for page_id, page_info in pages_dict.items():
            revisions = page_info.get('revisions', [])
            if revisions:
                rev = revisions[0]
                text = ""
                if '*' in rev:
                    text = rev['*']
                elif 'slots' in rev and 'main' in rev['slots'] and '*' in rev['slots']['main']:
                    text = rev['slots']['main']['*']
                    
                if text and len(text.strip()) > 0:
                    wiki_data.append({"title": title, "content": text})

with open('data/deepwoken_wiki.json', 'w', encoding='utf-8') as f:
    json.dump(wiki_data, f, indent=4)

print(f"Done! Saved {len(wiki_data)} pages.")
