/**
 *  Handles cards HTML elements and toggles it.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded cards.js file.");

    // Find all "card" element instances.
    let card = $('.card');

    // Loop through each card element on page.
    $(card).each(function() {
        // Add toggle to dropdown element click.
        let toggle = $(this).children('.toggle');
        let card = $(this);
        $(toggle).on('click', function() {
            $(card).toggleClass('active');
        });
    });
});
