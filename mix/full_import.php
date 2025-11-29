<?php
// full_import.php - Import produktów i kategorii do PrestaShop
ini_set('max_execution_time', 0);
ini_set('memory_limit', '1024M');
ini_set('display_errors', 1);
error_reporting(E_ALL);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>Start Importu</h1><hr>";
flush();

// --- KONFIGURACJA ---
$jsonProductsFile = dirname(__FILE__) . '/produkty.json';
$jsonCategoriesFile = dirname(__FILE__) . '/kategorie.json';
$localImagesDir = dirname(__FILE__) . '/img/zdjecia/';

// --- Sprawdzenie plików JSON ---
if (!file_exists($jsonProductsFile)) die("<h3 style='color:red'>Brak pliku produkty.json!</h3>");
if (!file_exists($jsonCategoriesFile)) die("<h3 style='color:red'>Brak pliku kategorie.json!</h3>");

$products = json_decode(file_get_contents($jsonProductsFile), true);
$categories = json_decode(file_get_contents($jsonCategoriesFile), true);

if (!$products) die("Błąd dekodowania produkty.json");
if (!$categories) die("Błąd dekodowania kategorie.json");

echo "Znaleziono " . count($categories) . " kategorii i " . count($products) . " produktów.<hr>";
flush();

// --- FUNKCJE ---
function cleanCatName($str) {
    $str = str_replace(['/', "\n", "\r", "\t"], '', $str);
    return trim($str);
}

function getOrCreateCategory($name, $parentId = 2) { // ID 2 = Home
    $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
            LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
            WHERE cl.name = "'.pSQL($name).'" 
            AND c.id_parent = '.(int)$parentId;
    $id = Db::getInstance()->getValue($sql);
    if ($id) return (int)$id;

    $c = new Category();
    $c->name = [1 => $name];
    $c->link_rewrite = [1 => Tools::link_rewrite($name)];
    $c->id_parent = $parentId;
    $c->active = 1;
    $c->id_shop_list = [1];
    if ($c->add()) {
        $existingGroups = Db::getInstance()->executeS('SELECT id_group FROM '._DB_PREFIX_.'category_group WHERE id_category = '.$c->id);
        $existingGroups = array_column($existingGroups, 'id_group');
        $groupsToAdd = array_diff([1,2,3], $existingGroups);
        if (!empty($groupsToAdd)) $c->addGroups($groupsToAdd);
    }
    return $c->id;
}

function addImageLocal($id_product, $imgUrl, $baseDir) {
    $filename = basename($imgUrl);
    $sourcePath = $baseDir . $filename;

    // 1. Pobierz z internetu jeśli brak lokalnie
    if (!file_exists($sourcePath) && filter_var($imgUrl, FILTER_VALIDATE_URL)) {
        if (@copy($imgUrl, $sourcePath)) {
            echo " [Pobrano z internetu: $filename] ";
        }
    }

    if (!file_exists($sourcePath)) {
        echo " [Brak pliku: $filename] ";
        return;
    }

    // 2. Konwersja do JPG jeśli nie JPEG
    $ext = strtolower(pathinfo($sourcePath, PATHINFO_EXTENSION));
    $tmpPath = $sourcePath;
    if ($ext !== 'jpg' && $ext !== 'jpeg') {
        $img = @imagecreatefromstring(file_get_contents($sourcePath));
        if (!$img) {
            echo " [Niepoprawny obraz: $filename] ";
            return;
        }
        $tmpPath = preg_replace('/\.\w+$/', '.jpg', $sourcePath);
        imagejpeg($img, $tmpPath, 90);
        imagedestroy($img);
        echo " [{$ext} -> JPG] ";
    }

    // 3. Dodanie do PrestaShop
    $image = new Image();
    $image->id_product = $id_product;
    $image->position = Image::getHighestPosition($id_product) + 1;
    $image->cover = ($image->position == 1);

    if (!$image->add()) return;

    $path = $image->getPathForCreation();
    $dir = dirname($path . '.jpg');
    if (!file_exists($dir)) mkdir($dir, 0777, true);

    if (@copy($tmpPath, $path . '.jpg')) {
        $types = ImageType::getImagesTypes('products');
        foreach ($types as $t) {
            ImageManager::resize($path . '.jpg', $path.'-'.stripslashes($t['name']).'.jpg', $t['width'], $t['height']);
        }
        echo " [FOTO] ";
    } else {
        $image->delete();
    }
}


// --- TWORZENIE KATEGORII ---
$categoryMap = [];
foreach ($categories as $cat) {
    $name = cleanCatName($cat['nazwa']);
    $id = getOrCreateCategory($name);
    $categoryMap[$name] = $id;
    echo "Kategoria: $name (ID: $id)<br>";
}
flush();

// --- IMPORT PRODUKTÓW ---
// Testowa partia (np. 5 produktów)
$testBatch = array_slice($products, 0, 5);
$counter = 0;
foreach ($products as $prod) {
    $counter++;
    $productName = trim($prod['nazwa']);

    // Sprawdzenie duplikatu
    $exists = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    if ($exists) continue;

    $price = (float)str_replace([',',' zł',' '], ['.','',''],$prod['cena'] ?? 0);
    $rawDesc = strip_tags($prod['opis'] ?? '');
    $shortDesc = mb_strlen($rawDesc) > 100 ? mb_substr($rawDesc,0,100,'UTF-8').'...' : $rawDesc;

    // Kategorie produktu
    $categoriesToAssign = [];
    if (isset($prod['kategoria']) && is_array($prod['kategoria'])) {
        foreach ($prod['kategoria'] as $catRaw) {
$catName = cleanCatName($catRaw);

// pomiń puste linie (czasem JSON ma "\n" jako kategoria)
if ($catName === '') continue;

if (!isset($categoryMap[$catName])) {
    $categoryMap[$catName] = getOrCreateCategory($catName);
}
$categoriesToAssign[] = $categoryMap[$catName];
        }
    }
    $defaultCategory = end($categoriesToAssign) ?: 2;

    // Tworzenie produktu
    $product = new Product();
    $product->name = [1 => $productName];
    $product->link_rewrite = [1 => Tools::link_rewrite($productName)];
    $product->price = $price;
    $product->id_category_default = $defaultCategory;
    $product->description = [1 => $prod['opis'] ?? ''];
    $product->description_short = [1 => $shortDesc];
    $product->active = 1;
    $product->show_price = 1;
    $product->id_shop_list = [1];

    if ($product->add()) {
        $product->addToCategories($categoriesToAssign);
        StockAvailable::setQuantity($product->id, 0, 100);

        echo "$counter. <b>$productName</b><br>";

        // Dodawanie zdjęć
        if (!empty($prod['zdjecia'])) {
            foreach ($prod['zdjecia'] as $imgUrl) {
                addImageLocal($product->id, $imgUrl, $localImagesDir);
            }
        }

    } else {
        echo "$counter. <b style='color:red'>Błąd zapisu:</b> $productName<br>";
        print_r($product->getErrors());
    }

    if ($counter % 5 == 0) { flush(); ob_flush(); }
}

// Regeneracja drzewa kategorii
Category::regenerateEntireNtree();
echo "<h1>IMPORT ZAKOŃCZONY</h1>";
?>
