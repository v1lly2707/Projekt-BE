{**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Academic Free License 3.0 (AFL-3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/AFL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/AFL-3.0 Academic Free License 3.0 (AFL-3.0)
 *}

{block name='head_extra'}
  <style>

    body {
        background-color: #000;
    }

    
    .dzik-top-bar {
        background: #1a1a1a;
        color: #fff;
        font-size: 14px;
        padding: 8px 0;
        text-align: center;
    }
    .dzik-promo-text .material-icons {
        font-size: 16px;
        margin-right: 5px;
        position: relative;
        top: 3px;
    }

    

.wk-login-grid-wrapper {
    display: flex;
    justify-content: center;
    gap: 30px; 
    max-width: 1100px;
    margin: 40px auto;
    padding: 20px;
    background: transparent !important; 
}

.wk-social-login,
.wk-main-login,
.wk-register-benefits {
    flex: 1; 
    padding: 30px;
    background: #fff; 
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
}

.wk-social-login h3,
.wk-main-login h3,
.wk-register-benefits h3 {
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 25px;
}

.wk-social-buttons button {
    width: 100%;
    margin-bottom: 15px;
    padding: 15px;
    font-weight: bold;
    border-radius: 4px;
    cursor: pointer;
}
.wk-facebook-btn {
    color: white !important;
    background: #3b5998 !important;
}
.wk-google-btn {
    color: white !important;
    background: #db4437 !important; 
}

.wk-main-login .btn-primary,
.wk-register-benefits .wk-register-btn {
    background: #000 !important;
    color: white !important;
    border: none !important;
    padding: 12px 25px;
    font-size: 16px;
    text-transform: none;
    border-radius: 4px;
    width: 100%; 
}
.wk-main-login .login-form-submit {
    text-align: center;
}

.wk-register-benefits ul {
    list-style: disc;
    padding-left: 20px;
    margin-top: 15px;
}
.wk-register-benefits li {
    margin-bottom: 10px;
}
    .wk-main-header {
        background: #1a1a1a !important; 
        padding: 15px 0;
    }
    
    .wk-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}
    
    .wk-col-logo {
    flex: 0 0 auto;
    background: transparent !important;
    margin-right: 20px;
    
}
.wk-col-logo img {
    max-height: 75px; 
    width: 80px;
    opacity: 1 !important; 
}
    

    .wk-col-menu {
        flex-grow: 1; 
        text-align: center; 
    }
    .wk-col-menu #top-menu {
        display: inline-flex !important;
        justify-content: center !important; 
        list-style: none;
        margin: 0;
        padding: 0;
    }
    .wk-col-menu #top-menu > li {
        display: block !important; 
        float: none !important; 
        padding: 0 5px;
    }
    .wk-col-menu #top-menu > li > a {
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        padding: 6px 10px;
        text-transform: uppercase;
        text-decoration: none;
        white-space: nowrap; 
    }

    .wk-col-icons {
    display: flex;
    justify-content: flex-end;
        align-items: center;
        color: #fff;
        font-size: 16px;
        flex-wrap: nowrap; 
        flex-basis: auto;
    }
    .wk-col-icons #search_widget {
        max-width: 110px; 
        margin-right: 10px;
        max-height: 45px;
    }
    .wk-col-icons #search_widget .input-group-btn > button,
    .wk-col-icons #search_widget input[type="text"] {
        background: #333 !important;
        border-color: #333 !important;
        color: #fff !important;
    }
    
    .wk-col-icons .header-nav-element {
        display: flex !important;
        align-items: center;
        margin-left: 10px;
    }

    .wk-col-icons .user-info > a > span,
    .wk-col-icons .cart-preview > a > span,
    .wk-col-icons .header-nav-element span {
        display: none !important;
    }

    .wk-col-icons .user-info a,
    .wk-col-icons .search-toggle,
    .wk-col-icons #_desktop_cart a {
        color: #fff !important;
    }


.wk-social-register-header {
    max-width: 500px;
    margin: 40px auto 30px auto;
    text-align: center;
}
.wk-social-register-header h3 {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 20px;
}

.wk-social-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
}

.wk-social-buttons a {
    flex-grow: 1; 
    padding: 10px 15px;
    font-weight: bold;
    border-radius: 4px;
    text-align: center;
    text-decoration: none;
    font-size: 15px;
}

.wk-facebook-btn {
    color: white !important;
    background: #3b5998 !important;
}
.wk-google-btn {
    color: #333 !important;
    background: #fff !important;
    border: 1px solid #ccc; 
}


.wk-register-main-form {
    max-width: 500px; 
    margin: 0 auto;
    padding: 20px 0;
    text-align: center;
}
.wk-register-main-form h2 {
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 30px;
    text-align: left;
}

.register-form .form-control {
    max-width: 100%; 
    border-radius: 4px;
    height: 45px;
}

.wk-register-final-btn {
    background: #000 !important;
    color: white !important;
    border: none !important;
    padding: 15px 40px;
    font-size: 18px;
    text-transform: none;
    border-radius: 4px;
    width: 100%; 
    max-width: 300px; 
    margin: 30px auto 0 auto;
}

  </style>
{/block}


{block name='header_banner'}
  <div class="header-nav dzik-top-bar">
    <div class="container">
      <div class="row">
        <div class="col-md-12 text-xs-center mobile-center-text">
          <span class="top-bar-text"><i class="material-icons">local_shipping</i> Darmowa dostawa od 300 zł</span>
        </div>
      </div>
    </div>
  </div>

  <div class="header-banner hidden-modules">
    {hook h='displayBanner'}
  </div>
{/block}

{block name='header_nav'}
  <nav class="header-nav hidden-modules" style="display:none;">
    <div class="container">
      <div class="row">
        <div class="hidden-sm-down">
          <div class="col-md-5 col-xs-12">
            {hook h='displayNav1'}
          </div>
          <div class="col-md-7 right-nav">
              {hook h='displayNav2'}
          </div>
        </div>
        <div class="hidden-md-up text-sm-center mobile">
          <div class="float-xs-left" id="menu-icon">
            <i class="material-icons d-inline">&#xE5D2;</i>
          </div>
          <div class="float-xs-right" id="_mobile_cart"></div>
          <div class="float-xs-right" id="_mobile_user_info"></div>
          <div class="top-logo" id="_mobile_logo"></div>
          <div class="clearfix"></div>
        </div>
      </div>
    </div>
  </nav>
{/block}

{block name='header_top'}
  <div class="header-top wk-main-header">
    <div class="container">
       <div class="wk-header-row">

        <div class="wk-col-logo" id="_desktop_logo">
            {if $shop.logo_details}
              <a href="{$urls.base_url}">
                <img class="logo img-responsive" src="{$shop.logo_details.src}" alt="{$shop.name}" width="{$shop.logo_details.width}" height="{$shop.logo_details.height}">
              </a>
            {else}
              <h1><a href="{$urls.base_url}">{$shop.name}</a></h1>
            {/if}
        </div>

        <div class="wk-col-menu">
            {hook h='displayNavFullWidth'}
        </div>

        <div class="wk-col-icons">
            {* 3a. Wyszukiwarka *}
            {hook h='displayTop'}
            
            <div id="_desktop_user_info" class="header-nav-element">
                {hook h='displayNav2'}
            </div>
            
            <div id="_desktop_cart" class="header-nav-element">
                {hook h='displayShoppingCart'}
            </div>

        </div>

      </div>
       <div id="mobile_top_menu_wrapper" class="row hidden-md-up" style="display:none;">
         <div class="js-top-menu mobile" id="_mobile_top_menu"></div>
         <div class="js-top-menu-bottom">
           <div id="_mobile_currency_selector"></div>
           <div id="_mobile_language_selector"></div>
           <div id="_mobile_contact_link"></div>
         </div>
       </div>
    </div>
  </div>
{/block}