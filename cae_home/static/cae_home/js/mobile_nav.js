/**
 *  Handles showing and hiding of nav in mobile mode.
 */


// Wait for full page load.
$(document).ready(function() {
    console.log("Loaded mobile_nav.js file.");

    var mobile_icon = $('.mobile-nav-icon');
    var main_nav = $('.nav-header-main > ul').clone();

    console.log(mobile_icon);
    console.log(main_nav);

    // Mobile Icon click handling.
    mobile_icon.on("click", function() {
        console.log("Mobile icon clicked.");
        var mobile_nav_overlay = "<div class='mobile-nav-overlay'><nav></nav></div>";
        $("body").prepend(mobile_nav_overlay);
        $("body .mobile-nav-overlay nav").append(main_nav);
    });


    // Nav overlay click handling.
    $(document).on("click", ".mobile-nav-overlay", function() {
        console.log("Overlay Clicked.");
        $(this).remove(".mobile-nav-overlay");
    });

    $(document).on("click", ".mobile-nav-overlay nav", function(event) {
        event.stopPropagation();
    });

});
