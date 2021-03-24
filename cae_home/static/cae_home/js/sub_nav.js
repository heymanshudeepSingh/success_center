/**
 *  Handles showing of "sub nav" element if not empty.
 */


// Wait for full page load.
$(document).ready(function() {
    window.cae_vars['nav__subNavContainer'] = $('header .sub-nav')[0];

    // Check if element contains any children. If so, display. Otherwise keep hidden.
    if ($(window.cae_vars['nav__subNavContainer']).children().length > 0) {
        $(window.cae_vars['nav__subNavContainer']).css('display', '');
    }
});
