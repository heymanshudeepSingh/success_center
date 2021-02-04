/**
 *  Handles fadeout and removal of status messages.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log("Loaded status_messages.js file.");

    // Get all status message containers (usualy, there should only be one, other than CSS examples page).
    let message_containers = $('.cae-status-message-container');

    // Set for all message containers.
    $(message_containers).each(function() {

        // Get dom elements of all message exit buttons.
        let message_exit_buttons = $(this).children('.message').children('.exit');

        // Add handling for each message button.
        message_exit_buttons.each(function() {
            // Add click handling to each message exit button.
            $(this).on("click", function() {

                // Select parent message of clicked exit button.
                let exit_parent = $(this).parents('.message');

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

});



/**
 * Generates a status message on page.
 *  :param message: Message to show to user.
 *  :param status_type: Type of message to send.
 *  :return: None on success or string on bad status_type.
 */
function generateStatusMessage(message, status_type) {

    console.log('starting message function');

    // Validate status type.
    status_type = String(status_type).trim().toLowerCase();
    if (
            (status_type != 'primary') &&
            (status_type != 'secondary') &&
            (status_type != 'info') &&
            (status_type != 'success') &&
            (status_type != 'warning') &&
            (status_type != 'error') &&
            (status_type != 'danger')
        ) {
        return 'Unknown status type. Recieved "' + status_type + '".';
    }

    // Find all message containers.
    let message_containers = $('.cae-status-message-container');

    // Create message element.
    let new_message = $("<li class=\"message " + status_type + "\"></li>");
    new_message.append($("<p>" + message + "</p>"));
    new_message.append($("<p class=\"exit\">x</p>"));

    // Send message to all message containers.
    $(message_containers).each(function() {

        // Append element to container.
        $(this).append(new_message);

    });
}
