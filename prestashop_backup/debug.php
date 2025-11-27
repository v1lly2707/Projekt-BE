<?php
// debug.php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
ini_set('max_execution_time', 0);

require(dirname(__FILE__) . '/config/config.inc.php');
require(dirname(__FILE__) . '/init.php');

echo "<h1>Start diagnostyki</h1>";

// 1. Sprawdzenie czy plik istnieje
$plikProdukty = 'produkty.json';
if (!file_exists($plikProdukty)) {
    die("<h2 style='color:red'>BŁĄD: Nie widzę pliku $plikProdukty w katalogu " . getcwd() . "</h2>");
} else {
    echo "<p style='color:green'>Plik $plikProdukty znaleziony.</p>";
}

// 2. Próba odczytu
$json = file_get_contents($plikProdukty);
$produkty = json_decode($json, true);

if ($produkty === null) {
    die("<h2 style='color:red'>BŁĄD: Plik JSON jest uszkodzony lub pusty.</h2>");
}

echo "<p>Znaleziono " . count($produkty) . " produktów w pliku.</p>";

// 3. Próba dodania pierwszych 5 produktów (TESTOWO)
$licznik = 0;
foreach ($produkty as $prodData) {
    if ($licznik >= 5) break; // Dodajemy tylko 5 sztuk na próbę
    
    echo "<hr>Przetwarzam: " . $prodData['nazwa'] . "<br>";
    
    // Czyszczenie ceny
    $cenaRaw = str_replace([' zł', ' ', '&nbsp;'], '', $prodData['cena']); // Usuwa spacje i "zł"
    $cenaRaw = str_replace(',', '.', $cenaRaw); // Zamienia przecinek na kropkę
    $cena = (float)$cenaRaw;
    
    echo "Cena po naprawie: $cena <br>";

    $product = new Product();
    $product->name = [1 => $prodData['nazwa']]; // Zakładamy język ID 1
    $product->link_rewrite = [1 => Tools::link_rewrite($prodData['nazwa'])];
    $product->price = $cena;
    $product->id_category_default = Configuration::get('PS_HOME_CATEGORY');
    $product->active = 1;
    $product->redirect_type = '404';
    $product->minimal_quantity = 1;
    $product->show_price = 1;
    $product->description = [1 => "Opis testowy"]; // Uproszczony opis
    
    // Przypisanie do kategorii Home
    $product->addToCategories([Configuration::get('PS_HOME_CATEGORY')]);

    try {
        if($product->add()) {
            echo "<b style='color:green'>SUKCES: Produkt dodany (ID: {$product->id})</b><br>";
            StockAvailable::setQuantity($product->id, 0, 100);
        } else {
            echo "<b style='color:red'>BŁĄD PRESTA: Nie udało się dodać produktu.</b><br>";
        }
    } catch (Exception $e) {
        echo "<b style='color:red'>WYJĄTEK: " . $e->getMessage() . "</b><br>";
    }
    
    $licznik++;
}

echo "<h1>Koniec testu</h1>";
?>
