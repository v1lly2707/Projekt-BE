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



{block name='page_content'}
  {block name='register_form_container'}
   
        {* 1. SEKCJA LOGOWANIA PRZEZ KONTA SPOŁECZNOŚCIOWE *}
        <div class="wk-social-register-header">
            <h3>{l s='Zaloguj się przez konto społecznościowe' d='Shop.Theme.Customeraccount'}</h3>
            <div class="wk-social-buttons">
                {* Użycie hooka do modułów logowania społecznościowego, jeśli są aktywne *}
                {$hook_create_account_top nofilter}
                
                {* Ręczne przyciski (CSS sprawi, że będą wyglądać jak na wzorze) *}
                <a href="#" class="btn btn-primary wk-facebook-btn"><i class="fa fa-facebook"></i> {l s='Zaloguj się przez Facebook' d='Shop.Theme.Customeraccount'}</a>
                <a href="#" class="btn btn-secondary wk-google-btn"><i class="fa fa-google"></i> {l s='Zaloguj się przez Google' d='Shop.Theme.Customeraccount'}</a>
            </div>
        </div>

        {* 2. GŁÓWNY FORMULARZ REJESTRACJI *}
        <section class="register-form wk-register-main-form">
            <h2>{l s='Rejestracja' d='Shop.Theme.Customeraccount'}</h2>
            
            {* Renderowanie pól formularza *}
            {render file='customer/_partials/customer-form.tpl' ui=$register_form}
            
            {* Zmiana przycisku i footera odbywa się w pliku customer-form.tpl *}
            
        </section>
        
        {* Ukrywamy oryginalny link "Masz już konto?", ponieważ użytkownik powinien już być na stronie logowania *}
        <div class="hidden-register-link" style="display:none;">
            <p>{l s='Already have an account?' d='Shop.Theme.Customeraccount'} <a href="{$urls.pages.authentication}">{l s='Log in instead!' d='Shop.Theme.Customeraccount'}</a></p>
        </div>

  {/block}
{/block}