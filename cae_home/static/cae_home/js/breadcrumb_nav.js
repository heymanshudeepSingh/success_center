/**
 *  Handles displaying of breadcrumb nav element.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded breadcrumb_nav.js file.");

    window.cae_vars['breadcrumbNav__container'] = $("#breadcrumb-nav");
    window.cae_vars['breadcrumb_element'] = $("#breadcrumb-nav ul");

    // Check if breadcrumb element is populated.
    if ($(window.cae_vars['breadcrumb_element']).children().length > 0) {

        // First, dynamically add separator elements into breadcrumb.

        // Add separator symbols between breadcrumb items.
        $("<li class='separator'>&nbsp;&lt;&nbsp;</li>").insertAfter($(window.cae_vars['breadcrumb_element'].children()));

        // Remove last separator, as it's trailing and doesn't separate anything useful.
        $(window.cae_vars['breadcrumb_element']).children().last().remove();

        // Display breadcrumb container to user.
        window.cae_vars['breadcrumbNav__container'].css("display", "flex");

        // Dynamically move/format BreadCrumb nav element on page load.

        // Check if page has h1 element (it should, but we make sure).
        let h1_element = $('h1');
        if (h1_element.length > 0) {
            window.cae_vars['breadcrumbNav__container'].detach().insertAfter(h1_element);
        }
    }
});
