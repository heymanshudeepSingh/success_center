/**
 *  Handles fadeout and removal of status messages.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded status_messages.js file.");

    // Get dom elements of all message exit buttons.
    var message_exit_buttons = $('#status-message-container').children('.message').children('.exit');

    // Add handling for each message button.
    message_exit_buttons.each(function() {
        // Add click handling to each message exit button.
        $(this).on("click", function() {
            // Select parent message of clicked exit button.
            exit_parent = $(this).parents('.message');

            // Set fade classes for clicked message.
            if (exit_parent.hasClass('fade-in')) {
                exit_parent.removeClass('fade-in');
            }
            exit_parent.addClass('fade-out');

            // Remove message after timer.
            setTimeout(function() {
                // Save message to console so user can still access it, if needed.
                console.log('Removed message:');
                console.log($(exit_parent).children().first().text().trim());
                exit_parent.detach();
            }, 700); // Wait 0.7 seconds.
        });
    });

});
