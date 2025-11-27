<div class="footer-container custom-wk-footer">
  <div class="container custom-footer-container">
    
    <div class="row">
      
      <div class="col-md-2 hidden-sm-down wrapper-logo-footer">
        <a href="{$urls.base_url}">
          <img src="{$shop.logo_details.src}" alt="{$shop.name}" class="logo img-fluid" style="filter: invert(1) brightness(2);">
        </a>
      </div>

      <div class="col-md-7 wrapper-links-footer">
        <div class="row">
          {block name='hook_footer'}
            {hook h='displayFooter'}
          {/block}
        </div>
      </div>

      <div class="col-md-3 wrapper-social-footer">
        
        <p class="h3 footer-heading">Obserwuj nas</p>
        <div class="social-icons-wk">
            <a href="#" target="_blank"><i class="fab fa-facebook-f"></i></a>
            <a href="#" target="_blank"><i class="fab fa-instagram"></i></a>
            <a href="#" target="_blank"><i class="fab fa-youtube"></i></a>
            <a href="#" target="_blank"><i class="fab fa-tiktok"></i></a>
        </div>

        <div class="opineo-badge-box">
             <div class="opineo-top">
                 <span class="op-small">KLIENCI</span>
                 <span class="op-big">NAS KOCHAJĄ!</span>
             </div>
             <div class="opineo-stars">
                 4.9/5 <span style="color:#003b6d">★★★★★</span>
             </div>
             <div class="opineo-logo">
                 <i class="material-icons" style="color:#55b046; vertical-align:middle;">check_circle</i> OPINEO<span style="font-size:9px">.pl</span>
             </div>
        </div>

      </div>
    </div>

    <div class="row footer-bottom-row">
      <div class="col-md-6">
        <p class="copyright">
          © {date('Y')} {$shop.name}
        </p>
      </div>
    </div>

  </div>
</div>