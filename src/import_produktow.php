<?php
// 2_import_produktow.php - Dodaje produkty do istniejących kategorii
ini_set('max_execution_time', 0);
ini_set('memory_limit', '512M');
ini_set('display_errors', 1);
error_reporting(E_ALL);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>ETAP 2: Import Produktów i Zdjęć</h1>";
flush();

$json = file_get_contents('produkty.json');
$produkty = json_decode($json, true);

$counter = 0;

foreach ($produkty as $prodData) {
    $counter++;
    $productName = trim($prodData['nazwa']);
    
    // Sprawdź duplikat
    $exists = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    if ($exists) {
        echo "$counter. Pomijam istniejący: $productName<br>";
        continue;
    }

    // --- ZNAJDOWANIE KATEGORII ---
    $parentId = 2; // Startujemy od Home
    $categoriesToAssign = [2]; 

    if (isset($prodData['kategoria']) && is_array($prodData['kategoria'])) {
        foreach ($prodData['kategoria'] as $catRaw) {
            $catName = trim(str_replace(['/', "\n", "\r", "\t"], '', $catRaw));
            if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

            // Szukamy ID tej kategorii (ona MUSI istnieć po Etapie 1)
            $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
                    LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
                    WHERE cl.name = "'.pSQL($catName).'" AND c.id_parent = '.(int)$parentId;
            $foundId = Db::getInstance()->getValue($sql);
            
            if ($foundId) {
                $parentId = $foundId; // Idziemy głębiej w drzewo
                $categoriesToAssign[] = $foundId;
            }
        }
    }
    
    // Ostatnie znalezione ID to kategoria główna
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
    $product->id_shop_list = [1]; 
    
    if($product->add()) {
        $product->addToCategories($categoriesToAssign);
        StockAvailable::setQuantity($product->id, 0, 100);
        
        echo "$counter. <b>DODANO:</b> $productName (Kat ID: $defaultCategory)<br>";
        
        // ZDJĘCIA
        if (!empty($prodData['zdjecia'])) {
            foreach ($prodData['zdjecia'] as $imgUrl) {
                addImage($product->id, $imgUrl);
            }
        }
    } else {
        echo "$counter. <b style='color:red'>BŁĄD:</b> $productName<br>";
    }
    
    if ($counter % 5 == 0) { flush(); ob_flush(); }
}

echo "<h1>KONIEC IMPORTU</h1>";

// --- FUNKCJA ZDJĘĆ ---
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
