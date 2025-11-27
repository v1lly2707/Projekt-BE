from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import string


# =============== TEST 1 ==========================

# ID kategorii w Prestashop
KATEGORIA_1_ID = 9
KATEGORIA_1_NAZWA = "art"
KATEGORIA_2_ID = 6
KATEGORIA_2_NAZWA = "accessories"

LICZBA_PRODOKTOW = 2
LICZBA_PRODOKTOW_NA_KATEGORIE = 1


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


# ================ TEST 2 ==================

SZUKANA_FRAZA = "framed"


def add_random_product_via_search(search_term):

    search_input = wait.until(EC.presence_of_element_located((By.NAME, "s")))
    search_input.clear()
    search_input.send_keys(search_term + Keys.ENTER)  # wpisanie frazy + Enter
    
    results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-miniature"))) # pobieranie wszystkich produktów, które mają w nazwie szukaną frazę
    if not results:
        raise ValueError(f"Brak wyników dla wyszukiwanej frazy: {search_term}")
    
    random_index = random.randint(0, len(results) - 1) # losujemy produkt (wymagania)
    selected_product = results[random_index]
    
    wait.until(EC.element_to_be_clickable(selected_product)).click()
    
    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart")))
    add_btn.click()
    
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))
        proceed_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#blockcart-modal a.btn.btn-primary"))
        )
        proceed_btn.click()
    except Exception:
        pass

    print(f"- Dodano losowy produkt spośród {len(results)} wyszukanych dla '{search_term}'")



# ================ TEST 3 ==================

LICZBA_USUWANYCH = 1

def remove_products_from_cart(n_to_remove):
    driver.get("https://localhost/koszyk")
    time.sleep(1)  # krótki sleep, żeby koszyk się w pełni załadował

    for i in range(n_to_remove):
        try:
            remove_buttons = driver.find_elements(By.CSS_SELECTOR, "a.remove-from-cart")
            if not remove_buttons:
                print("! Koszyk jest już pusty")
                break

            remove_btn = remove_buttons[0] # usuwamy od góry LICZBA_USUWANYCH produktów
            remove_btn.click()

            wait.until(EC.staleness_of(remove_btn))
            time.sleep(0.3)  # krótki sleep na odświeżenie koszyka
        except Exception as e:
            print(f"! Błąd przy usuwaniu produktu: {e}")
            break

    remaining = driver.find_elements(By.CSS_SELECTOR, "a.remove-from-cart")
    print(f"- Pozostało {len(remaining)} produktów w koszyku")



# ================ TEST 4 ==================

TESTOWE_IMIE = "Marek"
TESTOWE_NAZWISKO = "Kubale"
TESTOWE_HASLO = "haslo_maslo"
TESTOWA_DATA_URODZIN = "1945-12-31"

def random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "@example.com"

def register_new_account(driver):
    wait = WebDriverWait(driver, 10)
    driver.get("https://localhost/logowanie?create_account=1")

    TESTOWY_EMAIL = random_email()
    driver.find_element(By.CSS_SELECTOR, "label[for='field-id_gender-1']").click()# Pan
    driver.find_element(By.ID, "field-firstname").send_keys(TESTOWE_IMIE)
    driver.find_element(By.ID, "field-lastname").send_keys(TESTOWE_NAZWISKO)
    driver.find_element(By.ID, "field-email").send_keys(random_email())
    driver.find_element(By.ID, "field-password").send_keys(TESTOWE_HASLO)
    driver.find_element(By.ID, "field-birthday").send_keys(TESTOWA_DATA_URODZIN)

    driver.find_element(By.NAME, "customer_privacy").click() # a niech się zgodzi na wszystko
    driver.find_element(By.NAME, "psgdpr").click()
    driver.find_element(By.NAME, "optin").click()
    driver.find_element(By.NAME, "newsletter").click()

    driver.find_element(By.CSS_SELECTOR, "button.form-control-submit").click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.account")))
    print(f":) Konto utworzone: {TESTOWY_EMAIL}")



#================ TEST ZAMÓWIENIA ===============

TESTOWY_ADRES = "Za górami, za lasami"
TESTOWY_KOD_POCZTOWY = "77-777"
TESTOWE_MIASTO = "Gdańsk"

def order_from_cart():
    driver.get("https://localhost/koszyk?action=show")

    # koszyk
    print(" Jestem w koszyku")
    time.sleep(1)
    checkout_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary"))
    )
    checkout_btn.click()

    # adres
    print(" Jestem przy wpisywaniu adresu")
    driver.find_element(By.ID, "field-address1").send_keys(TESTOWY_ADRES)
    driver.find_element(By.ID, "field-postcode").send_keys(TESTOWY_KOD_POCZTOWY)
    driver.find_element(By.ID, "field-city").send_keys(TESTOWE_MIASTO)
    print(" Zatwierdzam dane")
    submit_btn = wait.until(
        EC.element_to_be_clickable((By.NAME, "confirm-addresses"))
    )
    submit_btn.click()

    # dostawa i sposób płatności
    print(" Jestem przy wybieraniu sposobu dostawy i płatności")

    # # OPCJA 1 - NIESKONFIGUROWANY SKLEP
    # # dostawa
    # driver.find_element(By.CSS_SELECTOR, "label[for='delivery_option_2']").click() # my carrier na ten moment, TODO
    # submit_btn = wait.until(
    #     EC.element_to_be_clickable((By.NAME, "confirmDeliveryOption"))
    # )
    # submit_btn.click()
    # # płatność
    # driver.find_element(By.CSS_SELECTOR, "label[for='payment-option-2']").click() # przelew na ten moment
    # driver.find_element(By.NAME, "conditions_to_approve[terms-and-conditions]").click()
    
    # order_btn = wait.until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR, "#payment-confirmation button"))
    # )
    # order_btn.click()
    # time.sleep(10)

    # OPCJA 2 - SKONFIGUROWANY SKLEP
    # dostawa
    driver.find_element(By.CSS_SELECTOR, "label[for='delivery_option_2']").click() # my carrier, ale ważne, żeby dodać jakiegoś jeszcze w ustawieniach
    submit_btn = wait.until(
        EC.element_to_be_clickable((By.NAME, "confirmDeliveryOption"))
    )
    submit_btn.click()
    # płatność
    driver.find_element(By.CSS_SELECTOR, "label[for='payment-option-3']").click() # płatność przy odbiorze
    driver.find_element(By.NAME, "conditions_to_approve[terms-and-conditions]").click()
    
    order_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#payment-confirmation button"))
    )
    order_btn.click()
    #time.sleep(10)

    print(" :) Zamówiono!")

    print("  Sprawdzam status zamówienia i pobieram fakturę")
    driver.get("https://localhost/historia-zamowien")
    first_order_row = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
    )
    status = first_order_row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
    print(f"   ✔ Status zamówienia: {status}")

    print("    Szukam linku do faktury...")
    time.sleep(10)
    invoice_link = None
    for _ in range(10):  # 10 prób
        driver.refresh()
        first_order_row = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
        )
        try:
            invoice_link = first_order_row.find_element(
                By.CSS_SELECTOR, "a[href*='controller=pdf-invoice']"
            )
            break
        except:
            pass

        time.sleep(1)

    if not invoice_link:
        raise Exception("! Brak faktury VAT dla tego zamówienia!")

    print("  Faktura dostępna → pobieram PDF")

    # Kliknięcie w link
    invoice_link.click()

    time.sleep(3)  # chwila na pobranie

    print("   Faktura pobrana.")
    
if __name__ == "__main__":
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import os

    chrome_options = Options()
    
    # 1. To jest ryzykowne, jeśli masz zwykłego Chrome. 
    # Zakomentuj to, żeby Selenium samo znalazło standardowego Google Chrome.
    # chrome_options.binary_location = "/snap/bin/chromium"

    # 2. Kluczowe flagi dla Linuxa
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    
    # 3. Tryb Headless (bez okna) - wymagany na serwerach bez ekranu.
    # Jeśli chcesz widzieć co się dzieje, zakomentuj linię poniżej:
    #chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--window-size=1920,1080") # Ważne w headless, żeby elementy nie były "poza ekranem"

    # 4. FIX NA PERMISSION ERROR / CRASH
    # Tworzymy lokalny folder na profil przeglądarki
    current_folder = os.getcwd()
    user_data_dir = os.path.join(current_folder, "chrome_user_data")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    # 5. Uruchomienie z Webdriver Managerem (automatycznie pobiera dobry sterownik)
    print("Uruchamianie sterownika Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Ustawienie timeoutu
    wait = WebDriverWait(driver, 10) # Zwiększyłem lekko czas oczekiwania

    try:
        print("========== TESTY 1-4 ==========")
        start = time.time()

        print("1. Test - dodanie 4 produktów z 2 kategorii")
        test_add_products_from_categories()

        print("2. Test - dodanie produktu poprzez wyszukiwanie")
        add_random_product_via_search(SZUKANA_FRAZA)

        print("3. Test - usunięcie produktów z koszyka")
        remove_products_from_cart(LICZBA_USUWANYCH)

        print("4. Test - założenie konta")
        register_new_account(driver)

        print("5. Test - złożenie zamówienia")
        order_from_cart()

        end = time.time()
        print(f"\n:D Testy zakończone pomyślnie w czasie {end - start:.3f} s")

    except Exception as e:
        print(f"\n!!! Wystąpił błąd podczas testów: {e}")
        # Opcjonalnie: zrób zrzut ekranu w momencie błędu
        driver.save_screenshot("blad_screenshot.png")
        raise e
    finally:
        driver.quit()