/**
 * Detects and initializes html elements with the select2 class.
 */


$(document).ready(function() {
    // Basic select2 form element.
    $('.form-widget-select2').select2();

    // Basic select2 form element, but with ability for user to create new entries in real time.
    $('.form-widget-select2-with-tagging').select2({
        tags: true,
        selectOnClose: true
    });

    // Multi-choice select2 form element.
    $('.form-widget-select2-multiple').select2();
});
