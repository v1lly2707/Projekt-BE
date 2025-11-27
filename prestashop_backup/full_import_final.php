<?php
// full_import_final.php - 2-FAZOWY IMPORT (Kategorie -> Produkty)
define('_PS_ADMIN_DIR_', getcwd());
require_once(dirname(__FILE__) . '/config/config.inc.php');
require_once(dirname(__FILE__) . '/init.php');

ini_set('max_execution_time', 0);
ini_set('memory_limit', '1024M');
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>START IMPORTU (2 FAZY)</h1>";
flush();

// --- KONFIGURACJA ---
$jsonFile = dirname(__FILE__) . '/produkty.json';
$localImagesDir = dirname(__FILE__) . '/img/'; // Tu szukamy zdjęć

if (!file_exists($jsonFile)) die("<h3 style='color:red'>Brak pliku produkty.json!</h3>");
$produkty = json_decode(file_get_contents($jsonFile), true);
if (!$produkty) die("Błąd JSON");

echo "Znaleziono " . count($produkty) . " produktów.<hr>";


// ==========================================
// FAZA 1: BUDOWANIE DRZEWA KATEGORII
// ==========================================
echo "<h3>FAZA 1: Tworzenie Kategorii...</h3>";

foreach ($produkty as $prodData) {
    if (!isset($prodData['kategoria']) || !is_array($prodData['kategoria'])) continue;

    $parentId = Configuration::get('PS_HOME_CATEGORY'); // Start od Home (2)

    foreach ($prodData['kategoria'] as $catRaw) {
        $catName = cleanString($catRaw);
        
        // Pomiń puste i "Strona główna"
        if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

        // Znajdź lub stwórz w AKTUALNYM rodzicu
        $catId = getOrCreateCategory($catName, $parentId);
        
        // Idziemy głębiej
        $parentId = $catId;
    }
}
// Przelicz drzewo po zakończeniu fazy 1
Category::regenerateEntireNtree();
echo "<span style='color:green'>Kategorie gotowe!</span><hr>";
flush();


// ==========================================
// FAZA 2: IMPORT PRODUKTÓW I ZDJĘĆ
// ==========================================
echo "<h3>FAZA 2: Dodawanie Produktów...</h3>";

$counter = 0;

foreach ($produkty as $prodData) {
    $counter++;
    $productName = trim($prodData['nazwa']);
    
    // 1. Sprawdź duplikat
    $exists = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    if ($exists) {
        // echo "Pomijam istniejący: $productName<br>";
        continue;
    }

    // 2. Ustal Kategorie (te same co w Fazie 1, ale teraz pobieramy ID)
    $parentId = Configuration::get('PS_HOME_CATEGORY');
    $categoriesToAssign = [$parentId]; 

    if (isset($prodData['kategoria']) && is_array($prodData['kategoria'])) {
        foreach ($prodData['kategoria'] as $catRaw) {
            $catName = cleanString($catRaw);
            if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

            // Pobieramy ID (kategoria MUSI już istnieć po Fazie 1)
            $catId = getCategoryByNameAndParent($catName, $parentId);
            
            if ($catId) {
                $parentId = $catId;
                $categoriesToAssign[] = $catId;
            }
        }
    }
    $defaultCategory = end($categoriesToAssign);

    // 3. Tworzenie Produktu
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
    $product->indexed = 1;
    $product->id_shop_list = [1]; 

    if ($product->add()) {
        $product->addToCategories($categoriesToAssign);
        StockAvailable::setQuantity($product->id, 0, 100);
        
        echo "$counter. <b>$productName</b> ";
        
        // 4. ZDJĘCIA (Z folderu lokalnego /img/)
        if (!empty($prodData['zdjecia'])) {
            foreach ($prodData['zdjecia'] as $imgUrl) {
                addImageLocal($product->id, $imgUrl, $localImagesDir);
            }
        }
        echo "<br>";
    } else {
        echo "<b style='color:red'>Błąd: $productName</b><br>";
    }
    
    if ($counter % 5 == 0) { flush(); ob_flush(); }
}

echo "<h1>KONIEC IMPORTU</h1>";


// --- FUNKCJE ---

function cleanString($str) {
    return trim(str_replace(['/', "\n", "\r", "\t"], '', $str));
}

function getOrCreateCategory($name, $parentId) {
    // Sprawdź czy jest
    $id = getCategoryByNameAndParent($name, $parentId);
    if ($id) return $id;

    // Nie ma -> Stwórz
    $c = new Category();
    $c->name = [1 => $name];
    $c->link_rewrite = [1 => Tools::link_rewrite($name)];
    $c->id_parent = $parentId;
    $c->active = 1;
    $c->id_shop_list = [1];
    $c->add();
    $c->addGroups([1, 2, 3]);
    return $c->id;
}

function getCategoryByNameAndParent($name, $parentId) {
    $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
            LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
            WHERE cl.name = "'.pSQL($name).'" AND c.id_parent = '.(int)$parentId;
    return (int)Db::getInstance()->getValue($sql);
}

function addImageLocal($id_product, $url, $baseDir) {
    $filename = basename($url);
    $sourcePath = $baseDir . $filename;

    // Obsługa spacji w nazwach
    if (!file_exists($sourcePath)) {
        $sourcePath = $baseDir . urldecode($filename);
    }

    if (!file_exists($sourcePath)) {
        echo " <span style='color:orange; font-size:0.8em'>[Brak pliku: $filename]</span> ";
        return;
    }

    $image = new Image();
    $image->id_product = $id_product;
    $image->position = Image::getHighestPosition($id_product) + 1;
    $image->cover = ($image->position == 1);
    
    if (!$image->add()) return;

    $path = $image->getPathForCreation();
    $dir = dirname($path . '.jpg');
    if (!file_exists($dir)) mkdir($dir, 0777, true);

    if (@copy($sourcePath, $path . '.jpg')) {
        $types = ImageType::getImagesTypes('products');
        foreach ($types as $t) {
            ImageManager::resize($path . '.jpg', $path.'-'.stripslashes($t['name']).'.jpg', $t['width'], $t['height']);
        }
        echo " <span style='color:green; font-weight:bold'>[FOTO]</span> ";
    } else {
        $image->delete();
    }
}
?>
