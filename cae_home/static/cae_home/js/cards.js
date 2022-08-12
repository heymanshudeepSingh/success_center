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
        // Add toggle elemenet to card.
        let card = $(this);
        let toggle = $('<div class="toggle"><ion-icon name="arrow-down-circle-outline"></ion-icon></div>');
        $(card).append(toggle);

        // Add dropdown element click.
        $(toggle).on('click', function() {
            $(card).toggleClass('active');
        });
    });
});
