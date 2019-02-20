/**
 *  Handles displaying and hiding of content overlay modal.
 *
 *  This file adds "overlay_container" and "overlay_modal" variables to be
 *  accessable by any JS files loaded after. Show/hite with show_overlay_modal()
 *  and hide_overlay_modal() functions, respectively.
 *
 *  To populate modal, append desired elements to the overlay_modal variable. Make
 *  sure to also clean appropriately, on hide.
 *
 *  Overlay elements default to hidden until show function is called.
 */


console.log('Started overlay_modal.js file.');

var overlay_container = $('#overlay-modal-container');
// console.log(overlay_container);
var overlay_modal = $('#overlay-modal');
// console.log(overlay_modal);


// Prevent clicks on modal from exiting overlay.
$(overlay_modal).click(function(event) {
    event.stopPropagation();
    // console.log("Overlay modal clicked.");
});

// Hide overlay when clicking on container.
$(overlay_container).click(function(event) {
    // console.log("Overlay container clicked.");
    hide_overlay_modal();
});

/**
 * Hide overlay modal.
 */
function hide_overlay_modal() {
    overlay_container.addClass('hidden');
    // console.log("Overlay modal hidden.");
}

function show_overlay_modal() {
    overlay_container.removeClass('hidden');
    // console.log("overlay modal shown.");
}
