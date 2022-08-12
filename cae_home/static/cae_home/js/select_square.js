/**
 * Logic for SelectSquare custom CSS element.
 * Behaves somewhat similarly to TabbedPanel element.
 */

// console.log('Loaded select_square.js');


// Iterate through each SelectSquare element found on page.
$('div.select-square').each(function() {

    // Save and detach root element children.
    let root_children = $(this).children('div').detach();

    // Initialize selection elements.
    let first_square = true;
    let square_name_array = [];
    let square_nav = $('<ul class="selectsquare-nav"></ul>');
    let square_content = $('<div class="selectsquare-content"></div>');

    // Loop through all found children.
    $(root_children).each(function() {

        // Create SelectSquare navigation element.
        let square_header = $(this).children(':first()').detach();
        let square_child = $('<li></li>').append(square_header);
        square_name_array.push($(square_header).text());

        // Set onclick square functionality.
        $(square_child).on('click', function() {
            window.cae_functions['selectSquare__toggleSelected'](this);
        });

        // Attach to parent.
        $(square_nav).append(square_child);

        // Create square content element.
        $(this).data('name', square_name_array.pop());
        $(this).appendTo(square_content);

        // Automatically display first tab by default.
        if (first_square) {
            $(square_child).addClass('selected');
            $(this).addClass('selected');
        }
        first_square = false;
    });

    // Put SelectSquare elements back into dom.
    $(square_nav).appendTo($(this));
    $(square_content).appendTo($(this));

});


/**
 * Handles selection square click events.
 */
window.cae_functions['selectSquare__toggleSelected'] = function(selected_square) {
    // Remove 'selected' class from all selectsquare-nav siblings and apply to self.
    $(selected_square).siblings('.selected').removeClass('selected');
    $(selected_square).addClass('selected');

    // Toggle square-content styles to show/hide.
    let square_content = $(selected_square).parent().parent().children('.selectsquare-content');
    $(square_content).children().each(function() {
        $(this).removeClass('selected');

        if ($(this).data('name') == $(selected_square).text()) {
            $(this).addClass('selected');
        }
    });
}
