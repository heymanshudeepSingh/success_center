/**
 *  Handles displaying of breadcrumb nav element.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded breadcrumb_nav.js file.");

    window.cae_vars['breadcrumbNav__container'] = $("#breadcrumb-nav");
    window.cae_vars['breadcrumb_element'] = $("#breadcrumb-nav ul");

    if ($(window.cae_vars['breadcrumb_element']).children().length > 0) {
        // Add separator symbols between breadcrumb items.
        $("<li>&nbsp;&gt;&nbsp;</li>").insertAfter($(window.cae_vars['breadcrumb_element'].children()));

        // Remove last separator, as it's trailing and doesn't separate anything useful.
        $(window.cae_vars['breadcrumb_element']).children().last().remove();

        // Display breadcrumb container to user.
        window.cae_vars['breadcrumbNav__container'].css("display", "flex");
    }
});
