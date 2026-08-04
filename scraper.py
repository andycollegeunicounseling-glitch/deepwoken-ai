import requests
import json
import os
import sys
import time

os.makedirs('data', exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

print("Starting full wiki download...")
url = "https://deepwoken.fandom.com/api.php"

# We use a Generator to get the page list AND the text content at the exact same time
params = {
    "action": "query",
    "format": "json",
    "generator": "allpages",
    "gaplimit": "50", # The max allowed by the API when downloading full text
    "prop": "revisions",
    "rvprop": "content",
    "rvslots": "main"
}

wiki_data = []
page_count = 0

# Loop until every single page is downloaded
while True:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"ERROR: Server returned status {response.status_code}")
        sys.exit(1)
        
    data = response.json()
    
    # Process the 50 pages from this batch
    pages = data.get('query', {}).get('pages', {})
    for page_id, page_info in pages.items():
        title = page_info.get('title', '')
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
                page_count += 1
                
    print(f"Downloaded {page_count} total pages so far...")
    
    # Check if there are more pages left on the wiki
    if 'continue' in data:
        # Automatically update the API token to grab the next 50 pages
        params.update(data['continue'])
        time.sleep(1) # Pause for 1 second so Fandom doesn't ban us for botting
    else:
        # If there is no 'continue' token, we have downloaded the entire wiki!
        break

print(f"\nFinished! Saving {len(wiki_data)} pages to file...")
with open('data/deepwoken_wiki.json', 'w', encoding='utf-8') as f:
    json.dump(wiki_data, f, indent=4)
    
print("Complete. Your engine data is ready.")
