from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import random

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

    print("2. Test - dodanie produktu poprzez wyszukiwanie")
    start = time.time()
    add_random_product_via_search(SZUKANA_FRAZA)
    driver.quit()
    end = time.time()
    print(f":) Test zakończony w czasie {end - start:.3f} s")

    
