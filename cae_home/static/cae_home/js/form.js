/**
 *  Handles form-specific JS.
 */


// Wait for full page load.
$(document).ready(function() {

    // Add confirmation boxes to all delete buttons.
    $(document).on('click', '.confirm-delete', function() {
        return confirm('Are you sure you wish to delete?')
    })

});
