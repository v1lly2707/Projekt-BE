<?php
// local_import_final.php - Wersja: JSON w roocie, Zdjęcia w /img/
define('_PS_ADMIN_DIR_', getcwd());
require_once(dirname(__FILE__) . '/config/config.inc.php');
require_once(dirname(__FILE__) . '/init.php');

// Ustawienia dla dużego importu
ini_set('max_execution_time', 0);
ini_set('memory_limit', '1024M');
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>Start Importu (Proste Ścieżki)</h1>";
flush();

// --- 1. KONFIGURACJA ŚCIEŻEK (Tak jak prosiłaś) ---
$baseDir = dirname(__FILE__) . '/'; // Główny katalog
$jsonFile = $baseDir . 'produkty.json'; // Plik JSON luzem w głównym
$imagesDir = $baseDir . 'img/'; // Zdjęcia w folderze img

// Diagnostyka ścieżek
if (!file_exists($jsonFile)) {
    die("<h3 style='color:red'>BŁĄD: Nie widzę pliku produkty.json w katalogu głównym ($jsonFile)</h3>");
}
// Folder img w Preście zawsze istnieje, ale upewnijmy się
if (!is_dir($imagesDir)) {
    die("<h3 style='color:red'>BŁĄD: Nie widzę folderu img ($imagesDir)</h3>");
}

$content = file_get_contents($jsonFile);
$produkty = json_decode($content, true);

if (!$produkty) die("Błąd dekodowania JSON. Sprawdź czy plik jest poprawny.");

echo "Ścieżka JSON: $jsonFile <br>";
echo "Ścieżka Zdjęć: $imagesDir <br>";
echo "Znaleziono " . count($produkty) . " produktów.<hr>";

$counter = 0;

// --- 2. PĘTLA IMPORTU ---
foreach ($produkty as $prodData) {
    $counter++;
    $productName = trim($prodData['nazwa']);
    
    // A. Sprawdź czy produkt już jest
    $id_product = Db::getInstance()->getValue('SELECT id_product FROM '._DB_PREFIX_.'product_lang WHERE name = "'.pSQL($productName).'" AND id_lang = 1');
    
    if ($id_product) {
        echo "$counter. Aktualizacja ID: $id_product ($productName)... ";
        $product = new Product($id_product);
    } else {
        echo "$counter. <b>Nowy:</b> $productName... ";
        $product = new Product();
    }

    // B. Kategorie (Budowanie Drzewa)
    $parentId = Configuration::get('PS_HOME_CATEGORY'); 
    $categoriesToAssign = [$parentId]; 

    if (isset($prodData['kategoria']) && is_array($prodData['kategoria'])) {
        foreach ($prodData['kategoria'] as $catRaw) {
            $catName = trim(str_replace(['/', "\n", "\r", "\t"], '', $catRaw));
            if (empty($catName) || mb_strtolower($catName) == 'strona główna') continue;

            $catId = getOrCreateCategory($catName, $parentId);
