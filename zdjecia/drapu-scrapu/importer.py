import requests
import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

# --- Konfiguracja ---
TARGET_URL = "https://wkdzik.pl/produkty-dzik/energy"
BASE_URL = "https://wkdzik.pl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}
OUT_DIR = Path("results")
OUT_DIR.mkdir(exist_ok=True)
CSV_FILE = OUT_DIR / "dzik_energy_products.csv"
CSV_DELIMITER = ',' # Używamy przecinka dla uniwersalności
# --------------------


def safe_get(url):
    """Bezpieczne pobieranie strony z obsługą błędów."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd podczas pobierania {url}: {e}")
        return None

def collect_product_links_from_category(url):
    """Zbiera wszystkie unikalne linki do produktów ze strony kategorii, celując w znane bloki."""
    
    response = safe_get(url)
    if not response:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    product_links = set()

    # CELOWANIE W NAJBARDZIEJ PRAWDOPODOBNE LOKALIZACJE:
    # 1. Kontenery produktów z linkami <a> wewnątrz
    # 2. Bezpośrednie linki do produktów oznaczonych jako 'product-link'
    PRODUCT_LINK_SELECTORS = [
        "div.product-miniature a",
        "div.product-item a",
        "a.product-link",
        "a[href*='/product/']",
        "a[href*='/produkt/']"
    ]
    
    for selector in PRODUCT_LINK_SELECTORS:
        for a in soup.select(selector):
            href = a.get('href')
            if href and not href.startswith(("#", "javascript:")):
                 full_url = urljoin(BASE_URL, href)
                 # Usuń wszystkie parametry URL (np. ?id=123) aby mieć czysty link
                 full_url = full_url.split('?')[0]
                 product_links.add(full_url)
            
    # Usuwamy URL samej kategorii (jeśli się tam dostał)
    if url in product_links:
        product_links.remove(url)

    return list(product_links)

def parse_single_product_page(url):
    """Parsuje stronę pojedynczego produktu, wyodrębniając kluczowe dane."""
    
    response = safe_get(url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "lxml")
    data = {}
    data['url'] = url
    
    # 1. Nazwa Produktu (h1)
    h1 = soup.find("h1")
    data['name'] = (h1.get_text(strip=True) if h1 else None) or "Brak Nazwy"

    # 2. Cena
    data['price'] = ""
    price_el = soup.select_one(".product-price, .current-price, [itemprop='price']")
    
    if price_el:
        if price_el.name == 'meta' and price_el.get("content"):
            price = price_el["content"]
        else:
            price_text = price_el.get_text(" ", strip=True)
            m = re.search(r"([0-9]+(?:[.,][0-9]{1,2})?)\s*zł", price_text, re.I)
            if m:
                price = m.group(1).replace(",", ".")
        
        data['price'] = price
        
    # 3. SKU (Kod produktu)
    data['sku'] = ""
    sku_el = soup.find(lambda tag: tag.name in ["div", "span", "p"] and re.search(r"kod produktu|sku", (tag.get_text() or ""), re.I))
    if sku_el:
        sku_text = sku_el.get_text(" ", strip=True)
        data['sku'] = sku_text.split(':')[-1].strip()
        
    # 4. Opis
    data['description'] = ""
    desc_candidates = soup.select(".product-description-full, #description_short, [id*='opis']")
    if desc_candidates:
        data['description'] = "\n\n".join([c.get_text("\n", strip=True) for c in desc_candidates])
        
    # 5. Kategoria (Ustawienie ręczne dla importu)
    data['category'] = "NAPOJE" 
    
    # 6. Zdjęcia
    img_el = soup.select_one("img.js-qv-product-cover") or soup.select_one("img.img-fluid")
    data['image_urls'] = urljoin(BASE_URL, img_el.get('src') or "") if img_el and img_el.get('src') else ""

    return data

def save_to_csv(products_data_list):
    """Zapisuje listę słowników danych produktów do pliku CSV."""
    
    fieldnames = ["name", "url", "price", "sku", "description", "category", "image_urls"]
    
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=CSV_DELIMITER)
            
            writer.writeheader()
            writer.writerows(products_data_list)
            
        print(f"\n✅ Zapisano {len(products_data_list)} produktów do: {CSV_FILE.resolve()}")
        
    except Exception as e:
        print(f"❌ Błąd podczas zapisu do CSV: {e}")


if __name__ == "__main__":
    print(f"🚀 Uruchamiam scraper dla kategorii: {TARGET_URL}")
    
    # Krok 1: Zbieranie linków
    product_urls = collect_product_links_from_category(TARGET_URL)
    print(f"🔍 Znaleziono {len(product_urls)} unikalnych linków do produktów.")

    if not product_urls:
        print("Brak linków do dalszego parsowania.")
    else:
        all_products_data = []
        
        # Krok 2: Parsowanie każdego linku
        for url in tqdm(product_urls, desc="Parsowanie produktów"):
            product_data = parse_single_product_page(url)
            if product_data:
                all_products_data.append(product_data)

        # Krok 3: Zapis do CSV
        save_to_csv(all_products_data)
        
    print("\n--- Program zakończony ---")