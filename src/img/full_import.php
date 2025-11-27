<?php
// full_import_v4.php - Wersja Diagnostyczna
ini_set('max_execution_time', 0);
ini_set('memory_limit', '512M');
ini_set('display_errors', 1);
error_reporting(E_ALL);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>Start Importu V4 (Czyste Drzewo)</h1>";
flush();

// 1. Wczytanie JSON
$json = file_get_contents('produkty.json');
if (!$json) die("Brak pliku produkty.json");
$produkty = json_decode($json, true);
if (!$produkty) die("Błąd JSON");

echo "Znaleziono " . count($produkty) . " produktów.<hr>";

$counter = 0;

foreach ($produkty as $prodData) {
    $counter++;
    $productName = trim($prodData['nazwa']);
    
    // A. Sprawdzenie duplikatu
    $exists = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    if ($exists) {
        echo "$counter. Pomijam (istnieje): $productName<br>";
        continue;
    }

    // B. Budowanie Drzewa Kategorii
    // Startujemy od Home (ID 2)
    $parentId = Configuration::get('PS_HOME_CATEGORY'); 
    $categoriesToAssign = [$parentId]; 
    $pathString = "Home";

    if (isset($prodData['kategoria']) && is_array($prodData['kategoria'])) {
        foreach ($prodData['kategoria'] as $catRaw) {
            // Agresywne czyszczenie
            $catName = cleanCatName($catRaw);
            
            // Pomijamy puste i "Strona główna"
            if (empty($catName) || $catName == 'Strona główna') continue;

            // Szukamy/Tworzymy
            $catId = getOrCreateCategory($catName, $parentId);
            
            // Budujemy ścieżkę
            $parentId = $catId;
            $categoriesToAssign[] = $catId;
            $pathString .= " -> " . $catName . "($catId)";
        }
    }
    
    // Kategoria główna produktu (najgłębsza)
    $defaultCategory = end($categoriesToAssign);

    // C. Tworzenie produktu
    $price = (float)str_replace([',', ' zł', ' '], ['.', '', ''], $prodData['cena']);

    $product = new Product();
    $product->name = [1 => $productName];
    $product->link_rewrite = [1 => Tools::link_rewrite($productName)];
    $product->price = $price;
    $product->id_category_default = $defaultCategory;
    $product->description = [1 => $prodData['opis'] ?? ''];
    $product->description_short = [1 => substr(strip_tags($prodData['opis'] ?? ''), 0, 100).'...'];
    $product->redirect_type = '404';
    $product->minimal_quantity = 1;
    $product->show_price = 1;
    $product->active = 1;
    $product->indexed = 1; // Wymuś indeksację
    
    // Ważne: Dodajemy produkt, a potem kategorie
    if($product->add()) {
        // Przypisanie kategorii
        $product->addToCategories($categoriesToAssign);
        StockAvailable::setQuantity($product->id, 0, 100);
        
        echo "$counter. <b>$productName</b><br>";
        echo "&nbsp;&nbsp;-- Ścieżka: $pathString <br>";
        
        // D. Zdjęcia
        if (!empty($prodData['zdjecia'])) {
            foreach ($prodData['zdjecia'] as $imgUrl) {
                addImage($product->id, $imgUrl);
            }
        }
        echo "<br>";
    } else {
        echo "$counter. <b style='color:red'>Błąd zapisu:</b> $productName<br>";
    }
    
    if ($counter % 5 == 0) { flush(); ob_flush(); }
}

// Kluczowe: Regeneracja drzewa na końcu
Category::regenerateEntireNtree();
echo "<h1>KONIEC - Drzewo przeliczone.</h1>";


// --- FUNKCJE ---

function cleanCatName($str) {
    // Usuwa wszystko co nie jest literą, cyfrą, spacją lub myślnikiem
    // Ale zostawiamy polskie znaki
    $str = str_replace(['/', "\n", "\r", "\t"], '', $str);
    return trim($str);
}

function getOrCreateCategory($name, $parentId) {
    // Sprawdzamy po nazwie W KONKRETNYM RODZICU
    $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
            LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
            WHERE cl.name = "'.pSQL($name).'" 
            AND c.id_parent = '.(int)$parentId;
    
    $id = Db::getInstance()->getValue($sql);
    if ($id) return (int)$id;

    // Tworzymy nową
    $c = new Category();
    $c->name = [1 => $name];
    $c->link_rewrite = [1 => Tools::link_rewrite($name)];
    $c->id_parent = $parentId;
    $c->active = 1;
    $c->add();
    return $c->id;
}

function addImage($id_product, $url) {
    $filename = basename($url);
    $localPath = _PS_ROOT_DIR_ . '/img/tmp_import/' . $filename;
    $source = file_exists($localPath) ? $localPath : $url;

    $image = new Image();
    $image->id_product = $id_product;
    $image->position = Image::getHighestPosition($id_product) + 1;
    $image->cover = ($image->position == 1);
    
    if (!$image->add()) return;

    $path = $image->getPathForCreation();
    $dir = dirname($path . '.jpg');
    if (!file_exists($dir)) mkdir($dir, 0777, true);

    if (@copy($source, $path . '.jpg')) {
        $types = ImageType::getImagesTypes('products');
        foreach ($types as $t) {
            ImageManager::resize($path . '.jpg', $path.'-'.stripslashes($t['name']).'.jpg', $t['width'], $t['height']);
        }
        echo " [FOTO] ";
    } else {
        $image->delete();
    }
}
?>
