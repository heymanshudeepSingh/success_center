/**
 *  Handles cards HTML elements and toggles it.
 */

// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded status_messages.js file.");

    let card = $('.card');
    console.log('card');
    console.log(card);

    $(card).each(function() {
        let toggle = $(this).children('.content').children('.toggle');
        console.log(toggle);
        let card = $(this);
        $(toggle).on("click", function() {
            console.log("clicked");
            $(card).toggleClass("active");
        });
    });
});
