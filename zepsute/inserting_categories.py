import requests
import csv
from xml.etree import ElementTree as ET
import re

import urllib3
# Wyłączenie ostrzeżeń SSL, ponieważ używamy https na localhost (dozwolone tylko w środowiskach lokalnych)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFIGURACJA API I PLIKU ---
API_KEY = "6HGXHV1GWW9EFYVG6NPPUFVJM6C1I64L"
CSV_FILE_PATH = "scrapResults/products.csv"
CSV_DELIMITER = ',' 
DEFAULT_LANG_ID = '1'

# Ustalony BASE_URL (Zmieniłem na HTTP 8080, aby uniknąć konfliktów SSL/401)
BASE_URL = "http://localhost:8080/api" 
PRESTASHOP_URL = f"{BASE_URL}/products"

# SŁOWNIK MAPOWANIA KATEGORII (Nazwa z CSV -> ID w PrestaShop)
CATEGORY_MAP = {
    'NAPOJE': 12,  # Twoja ręcznie utworzona kategoria
    # Możesz dodać więcej ręcznie utworzonych kategorii:
    # 'UBRANIA': 5,
    # 'SUPLEMENTY': 6,
}
# --- KONIEC KONFIGURACJI ---

# Używamy klucza API jako użytkownika, hasło puste (HTTP Basic Auth)
auth_tuple = (API_KEY, '')

# --- FUNKCJE POMOCNICZE XML ---
def find_and_set_multilang_value(root, field_name, value, lang_id=DEFAULT_LANG_ID):
    field = root.find(f".//{field_name}")
    if field is not None:
        field.clear()
        lang_element = ET.SubElement(field, 'language', id=lang_id)
        lang_element.text = value

def find_and_set_value(root, field_name, value):
    field = root.find(f".//{field_name}")
    if field is not None:
        field.text = value

# ----------------------------------------------------------------------
## 1. Wczytywanie Danych z CSV
# ----------------------------------------------------------------------

def load_products_from_csv(file_path):
    """Wczytuje produkty z pliku CSV i mapuje nazwy kategorii na ID."""
    products = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=CSV_DELIMITER)
            
            # Weryfikacja nagłówków
            expected_headers = ['name', 'url', 'price', 'sku', 'description', 'attributes_json', 'image_paths', 'category']
            if not all(header in csv_reader.fieldnames for header in expected_headers):
                 print(f"❌ Błąd: Nagłówki w pliku CSV nie pasują do oczekiwanych.")
                 print(f"Wykryte: {csv_reader.fieldnames}")
                 return []
            
            print(f"✅ Nagłówki CSV zweryfikowane. Rozpoczynam parsowanie i mapowanie kategorii...")

            for i, row in enumerate(csv_reader):
                product_name = row.get("name", "Produkt bez nazwy")
                category_data = row.get("category", "").strip() # To może być nazwa lub ID

                # 1. Konwersja ceny
                try:
                    row['price'] = str(float(row['price'].strip().replace(',', '.')))
                except ValueError:
                    print(f"Ostrzeżenie (Wiersz {i+1}): Nieprawidłowa cena '{row.get('price')}' dla produktu {product_name}. Pomijam.")
                    continue
                
                # 2. MAPOWANIE KATEGORII NA ID
                category_id = None
                
                # A. Sprawdź, czy nazwa jest w mapie (priorytet)
                if category_data.upper() in CATEGORY_MAP:
                    category_id = CATEGORY_MAP[category_data.upper()]
                    print(f"Mapowanie: Przypisano ID **{category_id}** dla '{category_data}'")
                else:
                    # B. Spróbuj potraktować jako bezpośrednie ID
                    try:
                        category_id = int(category_data)
                    except ValueError:
                        print(f"❌ Błąd (Wiersz {i+1}): Nie znaleziono mapowania dla '{category_data}' i nie jest to numeryczne ID. Pomijam ten produkt.")
                        continue
                
                row['category_id'] = category_id
                products.append(row)
        
        print(f"\n--- Podsumowanie ---")
        print(f"✅ Załadowano {len(products)} produktów z pliku {file_path}.")
        return products
        
    except FileNotFoundError:
        print(f"❌ Błąd: Plik CSV nie został znaleziony pod ścieżką: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Wystąpił nieznany błąd podczas wczytywania CSV: {e}")
        return []

# ----------------------------------------------------------------------
## 2. Tworzenie XML i Wysyłanie Produktów
# ----------------------------------------------------------------------

def create_prestashop_product_xml(product):
    """Generuje poprawny XML dla nowego produktu PrestaShop."""
    schema_url = PRESTASHOP_URL + "?schema=blank"
    try:
        response = requests.get(schema_url, auth=auth_tuple, verify=False) 
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania schematu produktu: {e}")
        return None

    # MAPOWANIE DANYCH CSV NA POLA PRESTASHOP
    name = product.get("name")
    reference = product.get("sku")
    price = product.get("price")
    description = product.get("description")
    category_id = product.get("category_id")

    # Wypełnianie pól
    find_and_set_multilang_value(root, 'name', name)
    find_and_set_multilang_value(root, 'description', description)
    find_and_set_multilang_value(root, 'description_short', description) 

    find_and_set_value(root, 'reference', reference) 
    find_and_set_value(root, 'price', price)
    find_and_set_value(root, 'active', '1') 
    find_and_set_value(root, 'id_tax_rules_group', '1') 
    find_and_set_value(root, 'available_for_order', '1')
    find_and_set_value(root, 'show_price', '1')
    
    # Powiązanie z kategoriami
    associations = root.find('.//associations')
    if associations is not None:
        associations.clear()
        
        ET.SubElement(associations, 'id_category_default').text = str(category_id)
        
        categories_list = ET.SubElement(associations, 'categories')
        category_tag = ET.SubElement(categories_list, 'category')
        ET.SubElement(category_tag, 'id').text = str(category_id)

    xml_string = ET.tostring(root, encoding='utf-8', method='xml').decode()
    return xml_string

def add_products_to_prestashop(products):
    for product in products:
        print(f"\n--- Przygotowuję produkt: {product.get('name', 'Brak Nazwy')} ---")
        
        product_xml = create_prestashop_product_xml(product)
        if product_xml is None:
            continue

        try:
            headers = {'Content-Type': 'application/xml'}
            response = requests.post(
                PRESTASHOP_URL, 
                data=product_xml, 
                headers=headers, 
                auth=auth_tuple,
                verify=False
            )
            response.raise_for_status()

            new_product_root = ET.fromstring(response.content)
            new_id = new_product_root.find('.//product').get('id')
            print(f"✅ Sukces! Dodano produkt '{product['name']}' (SKU: {product['sku']}) z ID: **{new_id}**")

        except requests.exceptions.RequestException as e:
            print(f"❌ Błąd dodawania produktu '{product.get('name', 'Brak Nazwy')}': {e}")
            if hasattr(response, 'content'):
                print("Treść błędu z PrestaShop:")
                print(response.content.decode())

# --- Wykonanie Skryptu ---
if __name__ == "__main__":
    products_data = load_products_from_csv(CSV_FILE_PATH)
    if products_data:
        add_products_to_prestashop(products_data)