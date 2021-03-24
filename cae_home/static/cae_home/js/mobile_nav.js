/**
 *  Handles showing and hiding of nav in mobile mode.
 */


/**
 * Add appropriate font sizing based on mobile display or not.
 */
window.cae_functions['mobileNav__addFontSizingClasses'] = function() {
    let font_size_class = null;

    if ($(window).width() > window.cae_vars['mobileNav__windowCutoff']) {
        // Currently in desktop mode.
        font_size_class = 'font-size-' + user_site_option_desktop_font_size;
    } else {
        // Currently in mobile mode.
        font_size_class = 'font-size-' + user_site_option_mobile_font_size;
    }

    if (font_size_class != 'font-size-') {
        window.cae_vars['body'].removeClass('font-size-base');
        window.cae_vars['body'].addClass(font_size_class);
    }
}


/**
 * Remove all possible font-sizing classes from base element.
 */
window.cae_functions['mobileNav__removeFontSizingClasses'] = function() {
    window.cae_vars['body'].removeClass('font-size-xs font-size-sm font-size-base font-size-md font-size-lg font-size-xl');
}


/**
 * Hide mobile nav menu.
 */
window.cae_functions['mobileNav__hideMobileNav'] = function() {
    // console.log("Hiding mobile nav.");

    $(window.cae_vars['mobileNav__headerBottom']).css("display", "none");
    $(window.cae_vars['mobileNav__headerBottom']).empty();
}


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded mobile_nav.js file.");

    window.cae_vars['mobileNav__windowCutoff'] = 857;
    window.cae_vars['body'] = $('body');
    window.cae_vars['mobileNav__mobileIcon'] = $('.mobile-nav-icon');
    window.cae_vars['mobileNav__mainNav'] = $('.nav-header-main > ul').clone();
    window.cae_vars['mobileNav__headerBottom'] = $('.header-bottom');

    // Set initial font size classes.
    window.cae_functions['mobileNav__addFontSizingClasses']();


    /**
     * Mobile Icon click handling.
     */
    window.cae_vars['mobileNav__mobileIcon'].on("click", function() {
        // console.log("Mobile icon clicked.");

        if ($(".header-bottom").css("display") == "none") {
            // console.log("Showing mobile nav.");

            $(".header-bottom").append("<nav></nav>");
            $(".header-bottom nav").append(window.cae_vars['mobileNav__mainNav']);
            $(".header-bottom").css("display", "flex");
        } else {
            window.cae_functions['mobileNav__hideMobileNav']();
        }
    });


    // Hide nav on other element clicks.
    $("main").on("click", function(event) {
        window.cae_functions['mobileNav__hideMobileNav']();
    });

    $("footer").on("click", function(event) {
        window.cae_functions['mobileNav__hideMobileNav']();
    });


    /**
     * Detect window screen size change and make appropriate adjustments.
     */
     $(window).on('resize', function() {
        // Reset font sizing based on window.
        window.cae_functions['mobileNav__removeFontSizingClasses']();
        window.cae_functions['mobileNav__addFontSizingClasses']();

        // Toggle nav menu based on width.
        if ($(window).width() >= window.cae_vars['mobileNav__windowCutoff']) {
            window.cae_functions['mobileNav__hideMobileNav']();
        }
     });

});
