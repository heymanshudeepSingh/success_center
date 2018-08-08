/**
 *  Handles showing and hiding of nav in mobile mode.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log('Loaded mobile js.');

    var nav_buttons = $('.menu-icon');
    var mobile_navs = $('.page > header > div > nav');
    var main_nav_button = nav_buttons[0];
    var main_mobile_nav = mobile_navs[0];
    var side_nav_button = nav_buttons[1];
    var side_mobile_nav = mobile_navs[1];
    // console.log(main_nav_button);
    // console.log(side_nav_button);
    // console.log(main_mobile_nav);
    // console.log(side_mobile_nav);


    // Main nav icon click handling.
    $(main_nav_button).on("click", function(event) {
        event.preventDefault();
        console.log("Main nav icon clicked.");

        $(main_mobile_nav).toggleClass('expanded');
    });

    // Side nav icon click handling.
    $(side_nav_button).on("click", function(event) {
        event.preventDefault();
        console.log("Side nav icon clicked.");

        $(side_mobile_nav).toggleClass('expanded');
    });

});
