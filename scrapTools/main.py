import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import re

# ================= KONFIGURACJA =================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

OUTPUT_FOLDER = "rezultaty_scrapowania"
IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "zdjecia")
FILE_PRODUCTS = "produkty.json"
FILE_CATEGORIES = "kategorie.json"

# 0 = pobranie wszystkiego
DEBUG_LIMIT = 0

if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
if not os.path.exists(IMAGES_FOLDER): os.makedirs(IMAGES_FOLDER)



def sanitize_filename(name):
    name = str(name).replace(' ', '_').replace('/', '-').replace('"', '')
    return re.sub(r'(?u)[^-\w.]', '', name)


def clean_url(url):
    if '?' in url: return url.split('?')[0]
    return url


def get_category_urls():
    url = 'https://wkdzik.pl/console/integration/execute/name/GoogleSitemap/list/categories/locale/pl_PL/page/1'
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')
        urls = [loc.text.strip() for loc in soup.find_all('loc')]
        # Filtrujemy, żeby nie brać zdjęć
        return [u for u in urls if not ('.jpg' in u or '.png' in u)]
    except Exception as e:
        print(f"Błąd mapy kategorii: {e}")
        return []


def scrape_category_name(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        if response.status_code != 200: return None

        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.find('h1')

        return {
            "nazwa": h1.text.strip() if h1 else "Inne",
            "url": url
        }
    except Exception:
        return None


def get_product_urls():
    url = 'https://wkdzik.pl/console/integration/execute/name/GoogleSitemap/list/products/locale/pl_PL/page/1'
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')
        urls = []
        for loc in soup.find_all('loc'):
            link = loc.text.strip()
            if '.jpg' in link or '.png' in link or '/cache/' in link: continue
            urls.append(link)
        return urls
    except Exception as e:
        print(f"Błąd mapy produktów: {e}")
        return []


def scrape_product_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        if response.status_code != 200: return None

        soup = BeautifulSoup(response.text, 'html.parser')

        product = {
            "nazwa": "Brak_nazwy",
            "url": url,
            "cena": "Brak ceny",
            "opis": "Brak opisu",
            "atrybuty": {},
            "zdjecia": []
        }

        h1 = soup.find('h1')
        if h1: product["nazwa"] = h1.text.strip()

        price_box = soup.find(class_='price') or soup.find(attrs={"itemprop": "price"})
        if price_box: product["cena"] = price_box.text.strip()

        desc = soup.find(class_='product-description') or soup.find(attrs={"itemprop": "description"})
        if desc: product["opis"] = desc.get_text(separator=' ').strip()

        attrs_div = soup.find(class_='product-attributes')
        if attrs_div:
            for li in attrs_div.find_all('li'):
                txt = li.text.strip()
                if ':' in txt:
                    k, v = txt.split(':', 1)
                    product["atrybuty"][k.strip()] = v.strip()

        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            product["zdjecia"].append(og_image["content"])

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.lower().endswith(('.jpg', '.png', '.webp', '.jpeg')):
                if href.startswith('/'): href = 'https://wkdzik.pl' + href
                if href not in product["zdjecia"]:
                    product["zdjecia"].append(href)

        product["zdjecia"] = product["zdjecia"][:2]

        return product

    except Exception as e:
        print(f"Błąd przy produkcie {url}: {e}")
        return None


print("=== ETAP 1/3: Pobieranie KATEGORII ===")
cat_urls = get_category_urls()
categories_data = []
seen_cats = set()

for url in cat_urls:
    data = scrape_category_name(url)
    if data and data['nazwa'] not in seen_cats:
        categories_data.append(data)
        seen_cats.add(data['nazwa'])
    time.sleep(random.uniform(0.2, 0.5))

with open(os.path.join(OUTPUT_FOLDER, FILE_CATEGORIES), 'w', encoding='utf-8') as f:
    json.dump(categories_data, f, ensure_ascii=False, indent=4)
print(f"Zapisano {len(categories_data)} kategorii.")

print("\n=== ETAP 2/3: Pobieranie DANYCH PRODUKTÓW ===")
prod_urls = get_product_urls()
products_data = []

if DEBUG_LIMIT > 0:
    print(f"!!! TRYB TESTOWY: Pobieram tylko {DEBUG_LIMIT} produktów !!!")
    prod_urls = prod_urls[:DEBUG_LIMIT]

counter = 0
total = len(prod_urls)

for url in prod_urls:
    counter += 1
    if counter % 5 == 0 or counter == 1:
        print(f"Przetwarzam: {counter}/{total} | {(counter / total) * 100:.1f}%")

    data = scrape_product_details(url)

    if data and data['nazwa'] != "Brak_nazwy":
        products_data.append(data)

    time.sleep(random.uniform(0.5, 1.0))

with open(os.path.join(OUTPUT_FOLDER, FILE_PRODUCTS), 'w', encoding='utf-8') as f:
    json.dump(products_data, f, ensure_ascii=False, indent=4)
print(f"Zapisano dane {len(products_data)} produktów do JSON.")

print("\n=== ETAP 3/3: POBIERANIE ZDJĘĆ ===")
img_counter = 0

for product in products_data:
    clean_name = sanitize_filename(product['nazwa'])

    for idx, img_url in enumerate(product['zdjecia']):
        img_url = clean_url(img_url)


        ext = ".jpg"
        if ".png" in img_url: ext = ".png"
        if ".webp" in img_url: ext = ".webp"

        filename = f"{clean_name}_{idx}{ext}"
        filepath = os.path.join(IMAGES_FOLDER, filename)

        if not os.path.exists(filepath):
            try:
                r = requests.get(img_url, headers=HEADERS, stream=True)
                if r.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    img_counter += 1
            except Exception as e:
                print(f"Błąd pobierania {filename}: {e}")

            time.sleep(0.2)

print("\n" + "=" * 40)
print("PROCES ZAKOŃCZONY SUKCESEM!")
print(f"Folder z wynikami: {os.path.abspath(OUTPUT_FOLDER)}")
print(f"Pobrano łącznie {img_counter} zdjęć.")