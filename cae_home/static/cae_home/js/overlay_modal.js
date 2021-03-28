/**
 *  Handles displaying and hiding of content overlay modal.
 *
 *  This file adds "overlay_container" and "overlay_modal" variables to be
 *  accessable by any JS files loaded after. Show/hite with overlayModal__showModal()
 *  and hideModal() functions, respectively.
 *
 *  To populate modal, append desired elements to the overlay_modal variable. Make
 *  sure to also clean appropriately, on hide.
 *
 *  Overlay elements default to hidden until show function is called.
 */


// console.log('Started overlay_modal.js file.');


window.cae_vars['overlayModal__container'] = $('#overlay-modal-container');
window.cae_vars['overlayModal__modal'] = $('#overlay-modal');
// console.log(window.cae_vars['overlayModal__container']);
// console.log(window.cae_vars['overlay_modal']);


// Prevent clicks within modal from exiting overlay.
$(window.cae_vars['overlayModal__modal']).click(function(event) {
    event.stopPropagation();
    // console.log("Overlay modal clicked.");
});


// Hide overlay when clicking on outer container.
$(window.cae_vars['overlayModal__container']).click(function(event) {
    // console.log("Overlay container clicked.");
    window.cae_functions['overlayModal__hideModal']();
});


/**
 * Hide overlay modal.
 */
window.cae_functions['overlayModal__hideModal'] = function() {
    // console.log('Hiding overlay modal.');
    window.cae_vars['overlayModal__container'].addClass('hidden');
}


/**
 * Show overlay modal.
 */
window.cae_functions['overlayModal__showModal'] = function() {
    console.log('Showing overlay modal.');
    window.cae_vars['overlayModal__container'].removeClass('hidden');
}
