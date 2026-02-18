"""
Simplified Casa.it HTML test - minimal version to test scraping.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from curl_cffi import requests
from bs4 import BeautifulSoup
import re


# Load Italian proxy
with open('/home/pap/Desktop/SafeSquare/backend/rotating_proxies_ita.md', 'r') as f:
    line = f.readline().strip()
    parts = line.split(':')
    if len(parts) == 4:
        username, password, hostname, port = parts
        proxy_url = f"http://{username}:{password}@{hostname}:{port}"
        proxy = {'http': proxy_url, 'https': proxy_url}

print("Testing Casa.it scraping with Italian proxy...")
print(f"Proxy: {hostname}:{port}")

url = "https://www.casa.it/vendita/residenziale/firenze/"
print(f"\nURL: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.it/',
}

print("\nMaking request...")

try:
    session = requests.Session()
    response = session.get(
        url,
        headers=headers,
        proxies=proxy,
        timeout=30,
        impersonate="chrome110"
    )
    
    print(f"✅ Status: {response.status_code}")
    print(f"   Response size: {len(response.text)} bytes")
    
    # Save HTML
    with open('/app/casa_test.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   HTML saved to: /app/casa_test.html")
    
    # Quick parse test
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Try multiple patterns
    print("\n" + "="*60)
    print("SELECTOR TESTS:")
    print("="*60)
    
    articles = soup.find_all('article')
    print(f"\n<article> tags: {len(articles)}")
    
    listings = soup.find_all('div', class_=re.compile(r'listing', re.I))
    print(f"div.listing: {len(listings)}")
    
    cards = soup.find_all('div', class_=re.compile(r'card', re.I))
    print(f"div.card: {len(cards)}")
    
    links = soup.find_all('a', href=re.compile(r'/vendita/'))
    print(f"Links with /vendita/: {len(links)}")
    
    prices = soup.find_all(text=re.compile(r'€\s*[\d.,]+'))
    print(f"€ symbols: {len(prices)}")
    
    sizes = soup.find_all(text=re.compile(r'\d+\s*m[²q2]'))
    print(f"m² sizes: {len(sizes)}")
    
    print("\n" + "="*60)
    
    if len(links) > 0:
        print("\n✅ SUCCESS! Found listing data")
        print(f"Sample link: {links[0] if links else 'N/A'}")
    else:
        print("\n⚠️ No listing data found - Casa.it may have changed structure")
        print("   Check /app/casa_test.html for actual HTML")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
