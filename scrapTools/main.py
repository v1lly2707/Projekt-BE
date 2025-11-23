import os
import re
import time
import json
import csv
import hashlib
import urllib.parse
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm

BASE_URL = "https://wkdzik.pl"
HEADERS = {
    "User-Agent": "ResearchScraper/1.0 (+https://example.org)",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}
DELAY_SECONDS = 1.0

OUT_DIR = Path("results")
IMG_DIR = OUT_DIR / "images"
OUT_DIR.mkdir(exist_ok=True)
IMG_DIR.mkdir(exist_ok=True)


def safe_get(url, session, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt+1 == max_retries:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError("unreachable")

def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text, flags=re.U).strip().lower()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:150]

def abs_url(href):
    return urllib.parse.urljoin(BASE_URL, href)


def collect_category_links(session):

    homepage = safe_get(BASE_URL, session).text
    soup = BeautifulSoup(homepage, "lxml")

    structured_data = []

    menu_container = soup.select_one("nav, [id*='menu'], [class*='menu']")

    if not menu_container:
        print("UWAGA: Nie znaleziono automatycznie kontenera menu. Użyj F12 i zaktualizuj selektor 'menu_container'.")
        # Spróbuj znaleźć <ul> jako ostateczność
        menu_container = soup.find("ul")
        if not menu_container:
            print("BŁĄD KRYTYCZNY: Nie można znaleźć menu. Przerwanie zbierania kategorii.")
            return []


    top_level_items = menu_container.find_all("li", recursive=False)
    if not top_level_items:
        first_ul = menu_container.find("ul")
        if first_ul:
            top_level_items = first_ul.find_all("li", recursive=False)

    if not top_level_items:
        print("Nie znaleziono 'li' na pierwszym poziomie. Biorę wszystkie 'li'...")
        top_level_items = menu_container.find_all("li")

    seen_top_level_urls = set()

    for li_item in top_level_items:

        cat_link = li_item.find("a", recursive=False)
        if not cat_link:
            cat_link = li_item.find("a")

        if not cat_link:
            continue
        cat_name = (cat_link.get_text() or "").strip()
        cat_url = cat_link.get("href")

        if not cat_name or not cat_url or cat_url.startswith(("#", "javascript:")):
            continue

        full_cat_url = abs_url(cat_url)

        if full_cat_url in seen_top_level_urls:
            continue

        if any(w in cat_name.lower() for w in
               ["strona", "kontakt", "blog", "logowanie", "koszyk", "regulamin", "dostawa"]):
            continue

        cat_data = {
            "category_name": cat_name,
            "category_url": full_cat_url,
            "subcategories": []
        }

        submenu = li_item.find("ul")
        if submenu:
            sub_links = submenu.find_all("a")
            for sub_link in sub_links:
                sub_name = (sub_link.get_text() or "").strip()
                sub_url = sub_link.get("href")

                if not sub_name or not sub_url or sub_url.startswith(("#", "javascript:")):
                    continue

                cat_data["subcategories"].append({
                    "subcategory_name": sub_name,
                    "subcategory_url": abs_url(sub_url)
                })

        structured_data.append(cat_data)
        seen_top_level_urls.add(full_cat_url)

    all_sub_urls = set()
    for item in structured_data:
        for sub in item["subcategories"]:
            all_sub_urls.add(sub["subcategory_url"])

    final_list = []
    for item in structured_data:
        if item["category_url"] not in all_sub_urls:
            href_l = item["category_url"].lower()
            if not item["subcategories"] and not any(s in href_l for s in ["/produkty", "/kategoria", "/collections"]):
                print(f"Odrzucam '{item['category_name']}' (pusty, nie pasuje URL)")
                continue

            final_list.append(item)
        else:
            print(f"Filtruję '{item['category_name']}' (jest już podkategorią gdzie indziej)")

    return final_list

def collect_products_from_category(cat_name, cat_url, session):
    products = []
    page_url = cat_url
    p = 1
    while True:
        r = safe_get(page_url, session)
        soup = BeautifulSoup(r.text, "lxml")

        product_links = []
        for a in soup.select("a"):
            href = a.get("href")
            if not href: continue

            text = (a.get_text() or "").strip()
            if not text: continue

            if len(text) > 3 and len(text) < 200 and re.search(r"[A-Za-z0-9ĄĆĘŁŃÓŚŹŻąćęłńóśźż\-\®]", text):
                if any(w in text.lower() for w in ["strona", "kontakt", "blog", "logowanie", "koszyk", "katalog"]):
                    continue
                if href.startswith("javascript:") or href.startswith("#"):
                    continue
                full = abs_url(href)
                product_links.append((text, full))
        seen = set()
        uniq = []
        for name, url in product_links:
            if url in seen: continue
            seen.add(url)
            uniq.append((name, url))
        products.extend(uniq)
        next_link = None
        for a in soup.select("a"):
            if a.get_text() and a.get_text().strip().isdigit():
                pass
            if a.get("rel") and "next" in a.get("rel"):
                next_link = abs_url(a.get("href"))
                break
        if next_link:
            page_url = next_link
            p += 1
            time.sleep(DELAY_SECONDS)
            continue
        found_numeric = False
        for a in soup.select("a"):
            t = (a.get_text() or "").strip()
            if t == str(p+1):
                href = a.get("href")
                if href:
                    page_url = abs_url(href)
                    found_numeric = True
                    p += 1
                    time.sleep(DELAY_SECONDS)
                    break
        if found_numeric:
            continue
        break
    deduped = []
    seenu = set()
    for name,url in products:
        if url in seenu: continue
        seenu.add(url)
        deduped.append({"category": cat_name, "product_name_link_text": name, "product_url": url})
    return deduped


def parse_product_page(product_url, session):
    r = safe_get(product_url, session)
    soup = BeautifulSoup(r.text, "lxml")

    h1 = soup.find(["h1", "h2"])
    name = (h1.get_text(strip=True) if h1 else None) or ""

    price = ""
    text = soup.get_text(" ", strip=True)
    m = re.search(r"([0-9]+(?:[.,][0-9]{1,2})?)\s*zł", text)
    if m:
        price = m.group(1).replace(",", ".")
    else:
        meta_price = soup.select_one("meta[itemprop='price']")
        if meta_price and meta_price.get("content"):
            price = meta_price["content"]


    sku = ""
    sku_el = soup.find(string=re.compile(r"Kod produktu", re.I))
    if sku_el:
        parent = sku_el.parent
        sku = parent.get_text(" ", strip=True).replace("Kod produktu:", "").strip()


    desc = ""

    desc_candidates = soup.select(".opis, .product-description, #opis, [id*='opis'], [class*='opis']")
    if desc_candidates:
        desc = "\n\n".join([c.get_text("\n", strip=True) for c in desc_candidates])
    else:

        h = soup.find(lambda tag: tag.name in ["h2","h3","strong"] and "Opis" in tag.get_text())
        if h and h.next_sibling:
            desc = h.next_sibling.get_text("\n", strip=True) if hasattr(h.next_sibling, "get_text") else str(h.next_sibling)


    attributes = {}

    for dl in soup.select("dl"):
        dts = dl.find_all("dt")
        for dt in dts:
            dd = dt.find_next_sibling("dd")
            if dd:
                attributes[dt.get_text(strip=True)] = dd.get_text(strip=True)

    for tr in soup.select("table tr"):
        tds = tr.find_all(["td","th"])
        if len(tds) >= 2:
            k = tds[0].get_text(strip=True)
            v = tds[1].get_text(strip=True)
            if k:
                attributes[k] = v


    img_urls = []

    for img in soup.select("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        if src.strip().endswith(".svg"):
            continue
        full = abs_url(src)

        if "1px" in full or "placeholder" in full:
            continue
        img_urls.append(full)

    img_urls = list(dict.fromkeys(img_urls))


    return {
        "url": product_url,
        "name": name.strip(),
        "price": price,
        "sku": sku.strip(),
        "description": desc.strip(),
        "attributes": attributes,
        "image_urls": img_urls,
    }

def download_best_images(img_urls, product_slug, session, max_images=2):
    saved = []
    product_folder = IMG_DIR / product_slug
    product_folder.mkdir(parents=True, exist_ok=True)
    images_info = []
    for i, url in enumerate(img_urls):
        try:
            r = safe_get(url, session)
        except Exception as e:
            continue
        data = r.content
        try:
            im = Image.open(BytesIO(data))
            width, height = im.size
        except Exception:
            width, height = 0, len(data)
        h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
        fname = f"{i+1}_{h}{ext}"
        path = product_folder / fname
        with open(path, "wb") as f:
            f.write(data)
        images_info.append({"path": str(path), "url": url, "width": width, "height": height, "area": width*height if width and height else len(data)})
        time.sleep(0.2)

    images_info.sort(key=lambda x: x.get("area", 0), reverse=True)
    chosen = images_info[:max_images]
    return chosen

def main():
    session = requests.Session()

    structured_categories = collect_category_links(session)

    print(f"Znaleziono {len(structured_categories)} struktur kategorii głównej (próbka):")
    for item in structured_categories[:10]:
        print(f" - {item['category_name']} (zawiera {len(item['subcategories'])} podkategorii)")

    # ZAPISYWANIE KATEGORII I PODKATEGORII
    cat_json_path = OUT_DIR / "categories.json"
    with open(cat_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_categories, f, ensure_ascii=False, indent=2)
    print(f"Zapisano strukturę kategorii do: {cat_json_path}")

    all_products = []


    if not structured_categories:
        print("Nowa metoda nie znalazła kategorii. Używam rezerwowej...")
        structured_categories = [{
            "category_name": "Produkty (Fallback)",
            "category_url": BASE_URL + "/produkty-dzik",
            "subcategories": []
        }]

    # ZBIERANIE LINKÓW
    for cat_info in structured_categories:
        cat_name = cat_info["category_name"]
        cat_url = cat_info["category_url"]


        print(f"Produkty dla KATEGORII GŁÓWNEJ: '{cat_name}' -> {cat_url}")
        try:

            prods = collect_products_from_category(cat_name, cat_url, session)
            print(f"  -> znaleziono {len(prods)} linków do produktów (raw)")
            all_products.extend(prods)
            time.sleep(DELAY_SECONDS)
        except Exception as e:
            print(f"Nie udało się zebrać dla {cat_name}: {e}")

        for sub_info in cat_info["subcategories"]:
            sub_name = sub_info["subcategory_name"]
            sub_url = sub_info["subcategory_url"]

            full_cat_name = f"{cat_name} > {sub_name}"

            print(f"Zbieram produkty dla PODKATEGORII: '{full_cat_name}' -> {sub_url}")
            try:
                prods = collect_products_from_category(full_cat_name, sub_url, session)
                print(f"  -> znaleziono {len(prods)} linków do produktów (raw)")
                all_products.extend(prods)
                time.sleep(DELAY_SECONDS)
            except Exception as e:
                print(f"Nie udało się zebrać dla {full_cat_name}: {e}")

    seen = set()
    unique_products = []
    for p in all_products:
        if p["product_url"] in seen:
            continue
        seen.add(p["product_url"])
        unique_products.append(p)
    print(f"Produkty do parsowania: {len(unique_products)}")

    # LIMIT_PRODUKTOW = 3
    # unique_products = unique_products[:LIMIT_PRODUKTOW]
    # print(f"--- TEST: Ograniczono do {len(unique_products)} produktów ---")
    #

    # POBIERANIE DANYCH I ZDJĘĆ (GŁÓWNA PĘTLA)
    results = []
    for item in tqdm(unique_products, desc="Products"):
        url = item["product_url"]
        try:  # <-- SZEROKI BLOK TRY...EXCEPT

            parsed = parse_product_page(url, session)

            slug = slugify(parsed.get("name") or url)
            if not slug:
                slug = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]

            chosen_imgs = download_best_images(parsed.get("image_urls", []), slug, session, max_images=2)

            parsed["downloaded_images"] = chosen_imgs
            parsed["category_link_text"] = item.get("product_name_link_text")
            parsed["category"] = item.get("category")

            results.append(parsed)

        except Exception as e:
            # Jeśli cokolwiek się nie uda, wydrukuj błąd i przejdź dalej
            print(f"BŁĄD: Pominięto produkt {url} z powodu: {e}")
            continue  # Przejdź do następnego item w pętli tqdm

        # Czekaj tylko jeśli wszystko się udało
        time.sleep(DELAY_SECONDS)

    # ZAPISYWANIE WYNIKÓW (JSON i CSV)
    json_path = OUT_DIR / "products.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    csv_path = OUT_DIR / "products.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "url", "price", "sku", "description", "attributes_json", "image_paths", "category"])
        for r in results:
            writer.writerow([
                r.get("name", ""),
                r.get("url", ""),
                r.get("price", ""),
                r.get("sku", ""),
                r.get("description", ""),
                json.dumps(r.get("attributes", {}), ensure_ascii=False),
                ";".join([i["path"] for i in r.get("downloaded_images", [])]),
                r.get("category", "")  # Dodałem też kategorię do CSV
            ])
    print("Done. Results saved to:", json_path, csv_path)
    print("Categories saved to:", cat_json_path)
    print("Images under:", IMG_DIR)


if __name__ == "__main__":
    main()
