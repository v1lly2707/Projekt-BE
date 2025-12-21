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
* @author  PrestaShop SA and Contributors <contact@prestashop.com>
* @copyright Since 2007 PrestaShop SA and Contributors
* @license https://opensource.org/licenses/AFL-3.0 Academic Free License 3.0 (AFL-3.0)
*}
{extends file='page.tpl'}

{block name='page_title'}
 {l s='Panel klienta' d='Shop.Theme.Customeraccount'}
{/block}

{block name='page_content'}
    <div class="wk-login-grid-wrapper">

        {* 1. KOLUMNA MEDIA/SOCIAL LOGIN (LEWA STRONA) *}
        <section class="wk-social-login">
            <h3>{l s='Kontynuuj z' d='Shop.Theme.Customeraccount'}</h3>
            <div class="wk-social-buttons">
                {* Użycie hooka do automatycznego umieszczenia przycisków modułów Social Media, jeśli są aktywne *}
                {hook h='displayCustomerLoginFormAfter'}
                
                {* Ręczne przyciski HTML (widoczne tylko, jeśli włączysz style w CSS) *}
                <button class="btn btn-primary wk-facebook-btn"><i class="fa fa-facebook"></i> {l s='Zaloguj się przez Facebook' d='Shop.Theme.Customeraccount'}</button>
                <button class="btn btn-secondary wk-google-btn"><i class="fa fa-google"></i> {l s='Zaloguj się przez Google' d='Shop.Theme.Customeraccount'}</button>
            </div>
        </section>

        {* 2. KOLUMNA FORMULARZA LOGOWANIA (GŁÓWNY ŚRODEK) *}
        <section class="wk-main-login">
            <h3>{l s='Zaloguj się' d='Shop.Theme.Customeraccount'}</h3>
            {block name='login_form_container'}
                <section class="login-form">
                    {render file='customer/_partials/login-form.tpl' ui=$login_form}
                </section>
                {* Pozostawiamy ten hook dla kompatybilności, ale jego zawartość jest teraz na lewej kolumnie *}
                {block name='display_after_login_form'}
                {/block}
            {/block}
        </section>

        {* 3. KOLUMNA REJESTRACJI/KORZYŚCI (PRAWA STRONA) *}
        <div class="wk-register-benefits">
            <h3>{l s='Zarejestruj się' d='Shop.Theme.Customeraccount'}</h3>
            <p>{l s='Otrzymasz liczne dodatkowe korzyści:' d='Shop.Theme.Customeraccount'}</p>
            <ul>
                <li>{l s='podgląd statusu realizacji zamówień' d='Shop.Theme.Customeraccount'}</li>
                <li>{l s='podgląd historii zakupów' d='Shop.Theme.Customeraccount'}</li>
                <li>{l s='brak konieczności wprowadzania swoich danych przy kolejnych zakupach' d='Shop.Theme.Customeraccount'}</li>
                <li>{l s='możliwość otrzymania rabatów i kuponów promocyjnych' d='Shop.Theme.Customeraccount'}</li>
            </ul>
            {* Przycisk rejestracji *}
            <a href="{$urls.pages.register}" class="btn btn-primary wk-register-btn">
                {l s='Zarejestruj się' d='Shop.Theme.Customeraccount'}
            </a>
            
            {* Link do rejestracji             
            <div class="no-account" style="margin-top: 15px;">
                <a href="{$urls.pages.register}" data-link-action="display-register-form">
                    {l s='Nie masz konta? Zarejestruj się tutaj' d='Shop.Theme.Customeraccount'}
                </a>
            </div>
            *}
        </div>
    </div>
{/block}