/**
 *  Handles showing and hiding of nav in mobile mode.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded mobile_nav.js file.");

    var mobile_icon = $('.mobile-nav-icon');
    var main_nav = $('.nav-header-main > ul').clone();

    // console.log(mobile_icon);
    // console.log(main_nav);


    // Hide mobile nav menu.
    function hide_mobile_nav() {
        // console.log("Hiding mobile nav.");

        $(".header-bottom").css("display", "none");
        $(".header-bottom").empty();

    }


    // Mobile Icon click handling.
    mobile_icon.on("click", function() {
        // console.log("Mobile icon clicked.");

        if ($(".header-bottom").css("display") == "none") {
            // console.log("Showing movile nav.");

            $(".header-bottom").append("<nav></nav>");
            $(".header-bottom nav").append(main_nav);
            $(".header-bottom").css("display", "flex");
        } else {
            hide_mobile_nav();
        }
    });


    // Hide nav on other element clicks.
    $("main").on("click", function(event) {
        hide_mobile_nav();
    });

    $("footer").on("click", function(event) {
        hide_mobile_nav();
    });

});
