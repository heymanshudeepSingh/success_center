/**
 * Detects and initializes elements with flatpicker classes.
 */

// Wait for full page load.
$(document).ready(function() {

    // // DateTime picker widget.
    // $('.form-widget-datetime-picker').flatpickr({
    //     enableTime: true,
    //     dateFormat: "Y-m-d H:i:S",
    //     altFormat: "F j, Y H:i K",
    // });

    // Date picker widget.
    $('.form-widget-date-picker').flatpickr({
        altInput: true,
        dateFormat: "Y-m-d",
        altFormat: "F j, Y",
    });

    // Time picker widget.
    $('.form-widget-time-picker').flatpickr({
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i K",
    });
});
