/**
 * Detects and initializes elements with flatpicker classes.
 */

// Wait for full page load.
$(document).ready(function() {

    // // DateTime picker widget.
    // $('.form-widget-datetime-picker').flatpickr({
    //     enableTime: true,
    //     dateFormat: "Y-m-d H:i",
    //     altFormat: true,
    //     altFormat: "F j, Y H:i K",
    // });

    // Date picker widget.
    $('.form-widget-date-picker').flatpickr({
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
    });

    // Time picker widget.
    $('.form-widget-time-picker').flatpickr({
        noCalendar: true,
        enableTime: true,
        enableSeconds: true,

        minuteIncrement: 1,

        dateFormat: "H:i:s",
        altInput: true,
        altFormat: "h:i K",
    });
});
