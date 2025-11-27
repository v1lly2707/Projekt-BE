from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_add_product_to_cart():
    try:
        first_product = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-thumbnail"))
        )
        first_product.click()

        add_to_cart_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart"))
        )
        add_to_cart_btn.click()

        try:
            wait.until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))
            proceed_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#blockcart-modal a.btn.btn-primary")
                )
            )
            proceed_btn.click()
        except Exception:
            cart_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-link-action='view-cart']"))
            )
            cart_button.click()

        qty_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.js-cart-line-product-quantity"))
        )
        quantity = qty_input.get_attribute("value")

        assert quantity == "1", f"Oczekiwano ilości 1, a jest {quantity}"

        print(":) Test przeszedł pomyślnie: produkt dodany do koszyka.")

    finally:
        driver.quit()


if __name__ == "__main__":
    #konfiguracja okienka
    chrome_options = Options()
    chrome_options.binary_location = "/snap/bin/chromium"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://localhost")
    wait = WebDriverWait(driver, 8) #czekamy, aż się stronka odpali przed zaczęciem testu

    print("test 1 - dodanie produktu do koszyka")
    start = time.time()
    test_add_product_to_cart()
    end = time.time()
    print(f":) Test 1 przeprowadzony pomyślnie w czasie {end - start:.3f} s")

    
