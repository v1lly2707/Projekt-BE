<?php
// full_import_v7.php - DIAGNOSTYKA + FORCE SHOP
ini_set('max_execution_time', 0);
ini_set('memory_limit', '512M');
ini_set('display_errors', 1);
error_reporting(E_ALL);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>Start Importu V7 (Diagnostyka)</h1>";

// --- SPRAWDZENIE CZY ROOT I HOME ISTNIEJĄ ---
$root = new Category(1);
$home = new Category(2);
if (!Validate::isLoadedObject($root) || !Validate::isLoadedObject($home)) {
    die("<h2 style='color:red'>BŁĄD KRYTYCZNY: Baza danych jest uszkodzona. Brak kategorii ID 1 lub ID 2. Wykonaj SQL naprawczy.</h2>");
} else {
    echo "Status Bazy: <span style='color:green'>Root i Home istnieją. OK.</span><hr>";
}

// 1. Wczytanie JSON
$json = file_get_contents('produkty.json');
if (!$json) die("Brak pliku produkty.json");
$produkty = json_decode($json, true);
if (!$produkty) die("Błąd JSON");

echo "Znaleziono " . count($produkty) . " produktów.<br>";
flush();

$counter = 0;

foreach ($produkty as $prodData) {
    $counter++;
    $productName = trim($prodData['nazwa']);
    
    // Sprawdź duplikat
    $exists = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    if ($exists) {
        // echo "$counter. Pomijam istniejący.<br>"; 
        continue;
    }

    // --- LOGIKA KATEGORII ---
    $parentId = 2; // Home
    $categoriesToAssign = [2]; 
    $catDebug = "Home";

    if (isset($prodData['kategoria']) && is_array($prodData['kategoria'])) {
        foreach ($prodData['kategoria'] as $catRaw) {
            $catName = cleanCatName($catRaw);
            
            // Pomijamy puste i "Strona główna"
            if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

            // Tworzymy/Szukamy
            $catId = getOrCreateCategoryV7($catName, $parentId);
            
            if (!$catId) {
                echo "<b style='color:red'>BŁĄD: Nie udało się stworzyć kategorii '$catName'!</b><br>";
                continue;
            }

            $parentId = $catId;
            $categoriesToAssign[] = $catId;
            $catDebug .= " -> $catName ($catId)";
        }
    }
    
    $defaultCategory = end($categoriesToAssign);

    // --- PRODUKT ---
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
    $product->id_shop_list = [1]; // WYMUSZAMY SKLEP ID 1
    
    if($product->add()) {
        $product->addToCategories($categoriesToAssign);
        StockAvailable::setQuantity($product->id, 0, 100);
        
        echo "$counter. <b>$productName</b> <br> &nbsp;&nbsp; Kat: $catDebug<br>";
        
        if (!empty($prodData['zdjecia'])) {
            foreach ($prodData['zdjecia'] as $imgUrl) {
                addImage($product->id, $imgUrl);
            }
        }
    } else {
        echo "$counter. <b style='color:red'>BŁĄD ZAPISU PRODUKTU:</b> ".print_r($product->getErrors(), true)."<br>";
    }
    
    if ($counter % 5 == 0) { flush(); ob_flush(); }
}

echo "<hr><h3>Regeneracja Drzewa... (Może chwilę potrwać)</h3>";
Category::regenerateEntireNtree();
echo "<h1>KONIEC SUKCES</h1>";


// --- FUNKCJE ---

function cleanCatName($str) {
    $str = str_replace(['/', "\n", "\r", "\t"], '', $str);
    return trim($str);
}

function getOrCreateCategoryV7($name, $parentId) {
    // 1. Szukamy
    $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
            LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
            WHERE cl.name = "'.pSQL($name).'" AND c.id_parent = '.(int)$parentId;
    $id = Db::getInstance()->getValue($sql);
    
    if ($id) return (int)$id;

    // 2. Tworzymy
    $c = new Category();
    $c->name = [1 => $name];
    $c->link_rewrite = [1 => Tools::link_rewrite($name)];
    $c->id_parent = $parentId;
    $c->active = 1;
    $c->id_shop_list = [1]; // WAŻNE: Przypisanie do sklepu
    
    if ($c->add()) {
        return $c->id;
    } else {
        echo "<span style='color:red'>Błąd tworzenia kategorii: " . print_r($c->getErrors(), true) . "</span>";
        return false;
    }
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
    } else {
        $image->delete();
    }
}
?>
