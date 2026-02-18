"""
Casa.it HTML Inspector - Run this with proxies to identify actual selectors.

This script will:
1. Fetch a search results page using our proxy infrastructure
2. Save the HTML to a file for inspection
3. Attempt to parse with multiple selector patterns
4. Report which selectors work

Usage:
    python scripts/inspect_casa_html.py --municipality "Firenze" --output "casa_firenze.html"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers.casa_scraper import CasaScraper
from bs4 import BeautifulSoup
import re


def test_selector_patterns(html: str):
    """Test multiple selector patterns to find what works."""
    soup = BeautifulSoup(html, 'lxml')
    
    print("\n" + "="*60)
    print("TESTING SELECTOR PATTERNS")
    print("="*60)
    
    # Pattern 1: Common listing card classes
    patterns = [
        # Listing cards
        ("Listing cards (article tag)", soup.find_all('article')),
        ("Listing cards (div.listing)", soup.find_all('div', class_=re.compile(r'listing', re.I))),
        ("Listing cards (div.card)", soup.find_all('div', class_=re.compile(r'card', re.I))),
        ("Listing cards (div.property)", soup.find_all('div', class_=re.compile(r'property', re.I))),
        ("Listing cards (div.annuncio)", soup.find_all('div', class_=re.compile(r'annuncio', re.I))),
        ("Listing cards (li with data-id)", soup.find_all('li', attrs={'data-id': True})),
        
        # Links
        ("Links to listings (a with /vendita/)", soup.find_all('a', href=re.compile(r'/vendita/'))),
        
        # Prices
        ("Price spans", soup.find_all('span', class_=re.compile(r'price', re.I))),
        ("Price divs", soup.find_all('div', class_=re.compile(r'price', re.I))),
        ("Text with € symbol",soup.find_all(text=re.compile(r'€\s*[\d.,]+'))),
        
        # Sizes
        ("Sizes (text with m²)", soup.find_all(text=re.compile(r'\d+\s*m[²q2]'))),
        ("Sizes (span.size)", soup.find_all('span', class_=re.compile(r'size|surface|mq', re.I))),
    ]
    
    for name, results in patterns:
        count = len(results)
        print(f"\n{name}: {count} found")
        
        if count > 0 and count < 50:  # Show sample if reasonable number
            print(f"  Sample: {str(results[0])[:200]}...")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description='Inspect Casa.it HTML structure')
    parser.add_argument('--municipality', type=str, default='Firenze', help='Municipality to inspect')
    parser.add_argument('--output', type=str, default='casa_html_sample.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    print(f"Fetching Casa.it search results for {args.municipality}...")
    print("Using proxies for bot detection bypass...")
    
    try:
        scraper = CasaScraper()
        url = scraper.build_search_url(args.municipality, page=1)
        
        print(f"URL: {url}")
        
        response = scraper.make_request(url)
        html = response.text
        
        # Save HTML
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ HTML saved to: {args.output}")
        print(f"   File size: {len(html)} bytes")
        
        # Test selectors
        test_selector_patterns(html)
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print(f"1. Open {args.output} in a browser to inspect DOM structure")
        print("2. Identify the correct selectors from the test results above")
        print("3. Update app/scrapers/casa_scraper.py with correct selectors")
        print("4. Re-run this script to verify")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis is likely due to:")
        print("  - Proxy configuration issues")
        print("  - Casa.it blocking the proxy IPs")
        print("  - Network connectivity problems")
        print("\nTry running with different proxy settings in scraper_config.yaml")
    
    finally:
        if 'scraper' in locals():
            scraper.close()


if __name__ == "__main__":
    main()
