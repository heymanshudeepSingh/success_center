/**
 *  Handles showing of "sub nav" element if not empty.
 */


// Wait for full page load.
$(document).ready(function() {
    var sub_nav_container =  $('header .sub-nav')[0];
    console.log(sub_nav_container);
    console.log('Children: ' + $(sub_nav_container).children().length);

    // Check if element contains any children. If so, display. Otherwise keep hidden.
    if ($(sub_nav_container).children().length > 0) {
        $(sub_nav_container).css('display', '');
    }
});
