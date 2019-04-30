/**
 *  Handles showing and hiding of nav in mobile mode.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded mobile_nav.js file.");

    var mobile_window_cutoff = 869;

    var body = $('body');
    var mobile_icon = $('.mobile-nav-icon');
    var main_nav = $('.nav-header-main > ul').clone();
    var header_bottom = $('.header-bottom');

    // Set initial font size classes.
    add_font_sizing_classes();


    /**
     * Hide mobile nav menu.
     */
    function hide_mobile_nav() {
        // console.log("Hiding mobile nav.");

        $(header_bottom).css("display", "none");
        $(header_bottom).empty();
    }


    /**
     * Mobile Icon click handling.
     */
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


    /**
     * Add appropriate font sizing based on mobile display or not.
     */
    function add_font_sizing_classes() {

        if ($(window).width() > mobile_window_cutoff) {
            // Currently in desktop mode.
            font_size_class = 'font-size-' + user_site_option_desktop_font_size;
        } else {
            // Currently in mobile mode.
            font_size_class = 'font-size-' + user_site_option_mobile_font_size;
        }

        if (font_size_class != 'font-size-') {
            body.removeClass('font-size-base');
            body.addClass(font_size_class);
        }
    }


    /**
     * Remove all possible font-sizing classes from base element.
     */
    function remove_font_sizing_classes() {
        body.removeClass('font-size-xs font-size-sm font-size-base font-size-md font-size-lg font-size-xl');
    }


    /**
     * Detect window screen size change and make appropriate adjustments.
     */
     $(window).on('resize', function() {
        remove_font_sizing_classes();
        add_font_sizing_classes();
     });

});
