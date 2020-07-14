/**
 *  Handles displaying of breadcrumb nav element.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded breadcrumb_nav.js file.");

    var breadcrumb_container = $("#breadcrumb-nav");
    var breadcrumb_element = $("#breadcrumb-nav ul");

    if ($(breadcrumb_element).children().length > 0) {
        // Add separator symbols between breadcrumb items.
        $("<li>&nbsp;&gt;&nbsp;</li>").insertAfter($(breadcrumb_element.children()));

        // Remove last separator, as it's trailing and doesn't separate anything useful.
        $(breadcrumb_element).children().last().remove();

        // Display breadcrumb container to user.
        breadcrumb_container.css("display", "flex");
    }
});
