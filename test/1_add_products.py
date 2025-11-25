from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random

# ID kategorii w Prestashop
KATEGORIA_1_ID = 9
KATEGORIA_1_NAZWA = "art"
KATEGORIA_2_ID = 6
KATEGORIA_2_NAZWA = "accessories"

LICZBA_PRODOKTOW = 10
LICZBA_PRODOKTOW_NA_KATEGORIE = 5



def add_product_from_listing(product_num):
    products = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-miniature"))
    )

    if product_num < 1 or product_num > len(products):
        raise ValueError(f"Niepoprawny numer produktu: {product_num}. Na stronie jest {len(products)} produktów.")

    product = products[product_num - 1]  # indeksowanie od 0
    wait.until(EC.element_to_be_clickable(product)).click()

    quantity_to_add = random.randint(1, 3) # losujemy liczbę produktów
    print(f"    → Dodaję {quantity_to_add} sztuk tego produktu")

    try:
        qty_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name='qty'], input.js-cart-line-product-quantity")
            )
        )
        qty_input.click()
        qty_input.send_keys(Keys.CONTROL + "a")
        qty_input.send_keys(Keys.BACKSPACE)
        qty_input.send_keys(str(quantity_to_add))
    except Exception:
        print("⚠ Nie znaleziono pola ilości, używam domyślnej 1 sztuki")

    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart")))
    add_btn.click()

    # Obsługa modala lub fallback
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))
        proceed_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#blockcart-modal a.btn.btn-primary"))
        )
        proceed_btn.click()
    except Exception:
        try:
            cart_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-link-action='view-cart']"))
            )
            cart_btn.click()
        except Exception:
            pass


def test_add_products_from_categories():
    total_added = 0

    # Generowanie URL na podstawie ID kategorii i nazwy
    base_url = "http://localhost/{}-{}"
    category_ids = [KATEGORIA_1_ID, KATEGORIA_2_ID]
    category_names = [KATEGORIA_1_NAZWA, KATEGORIA_2_NAZWA]
    category_urls = [base_url.format(cat_id, cat_name) for cat_id, cat_name in zip(category_ids, category_names)]

    for cat_index, url in enumerate(category_urls):
        print(f"- Wchodzę do kategorii nr {cat_index + 1} (ID: {category_ids[cat_index]})")
        driver.get(url)
        #time.sleep(1)

        for i in range(1, LICZBA_PRODOKTOW_NA_KATEGORIE + 1):  # dodajemy produkty z każdej kategorii
            print(f"  - Dodaję produkt {i} z tej kategorii")
            add_product_from_listing(i)
            total_added += 1
            driver.get(url)
            #time.sleep(1)

    driver.get("https://localhost/koszyk")
    print(f"  Przekierowano do koszyka po dodaniu {total_added} produktów")
    #time.sleep(10)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.binary_location = "/snap/bin/chromium"
    #chrome_options.add_argument("--headless") # czy bez interfejsu (szybciej, tak zrobimy w wersji ostatecznej), czy z (wolniej, lepiej do testów)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://localhost")

    wait = WebDriverWait(driver, 8)

    print("1. Test - dodanie 4 produktów z 2 kategorii")
    start = time.time()
    test_add_products_from_categories()
    driver.quit()
    end = time.time()
    print(f":) Test zakończony w czasie {end - start:.3f} s")

    
