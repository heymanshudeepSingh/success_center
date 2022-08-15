/**
 * Logic for PrioritySelect custom CSS element.
 * Behaves somewhat similarly to TabbedPanel element.
 */

// console.log('Loaded priority_select.js');


// Iterate through each PrioritySelect element found on page.
$('div.priority-select').each(function() {

    // Save and detach root element children.
    let root_children = $(this).children('div').detach();

    // Initialize selection elements.
    let first_priority = true;
    let priority_name_array = [];
    let priority_nav = $('<ul class="priorityselect-nav"></ul>');
    let priority_content = $('<div class="priorityselect-content"></div>');

    // Loop through all found children.
    $(root_children).each(function() {

        // Create PrioritySelect navigation element.
        let priority_header = $(this).children(':first()').detach();
        let priority_child = $('<li></li>').append(priority_header);
        priority_name_array.push($(priority_header).text());

        // Set onclick priority functionality.
        $(priority_child).on('click', function() {
            window.cae_functions['prioritySelect__toggleSelected'](this);
        });

        // Attach to parent.
        $(priority_nav).append(priority_child);

        // Create priority content element.
        $(this).data('name', priority_name_array.pop());
        $(this).appendTo(priority_content);

        // Automatically display first tab by default.
        if (first_priority) {
            $(priority_child).addClass('selected');
            $(this).addClass('selected');
        }
        first_priority = false;
    });

    // Put PrioritySelect elements back into dom.
    $(priority_nav).appendTo($(this));
    $(priority_content).appendTo($(this));

});


/**
 * Handles priority select click events.
 */
window.cae_functions['prioritySelect__toggleSelected'] = function(selected_priority) {
    // Remove 'selected' class from all priorityselect-nav siblings and apply to self.
    $(selected_priority).siblings('.selected').removeClass('selected');
    $(selected_priority).addClass('selected');

    // Toggle priority-content styles to show/hide.
    let priority_content = $(selected_priority).parent().parent().children('.priorityselect-content');
    $(priority_content).children().each(function() {
        $(this).removeClass('selected');

        if ($(this).data('name') == $(selected_priority).text()) {
            $(this).addClass('selected');
        }
    });
}
