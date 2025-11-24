<?php
// 1_import_kategorii.php - Buduje tylko strukturę drzewa
ini_set('max_execution_time', 0);
ini_set('display_errors', 1);
error_reporting(E_ALL);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>ETAP 1: Budowanie Drzewa Kategorii</h1>";
flush();

$json = file_get_contents('produkty.json');
if (!$json) die("Brak pliku produkty.json");
$produkty = json_decode($json, true);

// Tablica, żeby nie przetwarzać tych samych ścieżek 100 razy
$processedPaths = [];

foreach ($produkty as $prodData) {
    if (!isset($prodData['kategoria']) || !is_array($prodData['kategoria'])) continue;

    // Budujemy unikalny klucz ścieżki, żeby nie dublować pracy
    $pathKey = json_encode($prodData['kategoria']);
    if (isset($processedPaths[$pathKey])) continue;
    $processedPaths[$pathKey] = true;

    // Startujemy od Home (ID 2)
    $parentId = 2;

    foreach ($prodData['kategoria'] as $catRaw) {
        // Czyszczenie nazwy
        $catName = trim(str_replace(['/', "\n", "\r", "\t"], '', $catRaw));
        
        // Pomijamy puste i Home
        if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

        // Szukamy lub tworzymy w AKTUALNYM rodzicu
        $catId = getOrCreateCategory($catName, $parentId);
        
        // Nowa kategoria staje się rodzicem dla następnej
        $parentId = $catId;
    }
    echo "Przetworzono ścieżkę dla: " . $prodData['nazwa'] . "<br>";
    flush();
}

// Ważne: Przeliczenie drzewa na koniec
Category::regenerateEntireNtree();
echo "<h1>KONIEC ETAPU 1 - Kategorie gotowe. Sprawdź w panelu!</h1>";


// --- FUNKCJA ---
function getOrCreateCategory($name, $parentId) {
    // Szukamy w bazie w konkretnym rodzicu
    $sql = 'SELECT c.id_category FROM '._DB_PREFIX_.'category c 
            LEFT JOIN '._DB_PREFIX_.'category_lang cl ON c.id_category = cl.id_category
            WHERE cl.name = "'.pSQL($name).'" AND c.id_parent = '.(int)$parentId;
    $id = Db::getInstance()->getValue($sql);
    
    if ($id) return (int)$id;

    // Tworzymy
    $c = new Category();
    $c->name = [1 => $name];
    $c->link_rewrite = [1 => Tools::link_rewrite($name)];
    $c->id_parent = $parentId;
    $c->active = 1;
    $c->id_shop_list = [1]; // Przypisanie do sklepu!
    
    if ($c->add()) {
        $c->addGroups([1, 2, 3]); // Widoczność dla wszystkich
        return $c->id;
    }
    return 2; // Fallback do Home
}
?>
