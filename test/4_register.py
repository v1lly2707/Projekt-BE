from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import string

#TESTOWY_EMAIL = "profesor.kubale@example.com"
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

    print("4. Test - założenie konta")
    start = time.time()
    register_new_account(driver)
    driver.quit()
    end = time.time()
    print(f":) Test zakończony w czasie {end - start:.3f} s")

    
