import requests

def probe():
    patterns = [
        "https://www.tecnocasa.it/annunci/immobili/lazio/roma/roma.html",
        "https://www.tecnocasa.it/vendita/immobili/lazio/roma/roma.html",
        "https://www.tecnocasa.it/vendita/appartamenti/lazio/roma/roma.html",
        "https://www.tecnocasa.it/annunci/residenziali/lazio/roma/roma.html",
        "https://www.tecnocasa.it/annunci/immobili/italia/lazio/roma/roma.html"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for url in patterns:
        try:
            r = requests.head(url, headers=headers, timeout=5)
            print(f"{r.status_code} | {url}")
        except Exception as e:
            print(f"ERR | {url} | {e}")

if __name__ == "__main__":
    probe()
