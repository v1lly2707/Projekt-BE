<div id="js-product-list-top" class="products-selection">
  <div class="wk-products-top-wrapper">

    {*LICZBA PRODUKTÓW *}
    <div class="wk-total-products">
      {if $listing.pagination.total_items > 1}
        <p>{l s='Liczba produktów:' d='Shop.Theme.Catalog'} 
           <span class="count-number">{$listing.pagination.total_items}</span>
        </p>
      {/if}
    </div>

    {* SORTOWANIE *}
    <div class="wk-sort-by">
        <span class="sort-label">Sortuj <i class="material-icons">expand_more</i></span>
        
        <div class="hidden-sort-wrapper">
           {include file='catalog/_partials/sort-orders.tpl' sort_orders=$listing.sort_orders}
        </div>
    </div>

    {* PAGINACJA *}
    <div class="wk-pagination-top">
      {block name='pagination'}
        {include file='catalog/_partials/pagination.tpl' pagination=$listing.pagination}
      {/block}
    </div>

  </div>
</div>
