/**
 * Logic for SelectScroll custom CSS element.
 * Behaves somewhat similarly to TabbedPanel element.
 */

// console.log('Loaded select_scroll.js');


// Iterate through each SelectScroll element found on page.
$('div.select-scroll').each(function() {

    // Save and detach root element children.
    let root_children = $(this).children('div').detach();

    // Initialize selection elements.
    let first_scroll = true;
    let scroll_name_array = [];
    let scroll_nav = $('<ul class="selectscroll-nav"></ul>');
    let scroll_content = $('<div class="selectscroll-content"></div>');

    // Loop through all found children.
    $(root_children).each(function() {

        // Create SelectScroll navigation element.
        let scroll_header = $(this).children('p:first()').detach();
        let scroll_child = $('<li></li>').append(scroll_header);
        scroll_name_array.push($(scroll_header).text());

        // Set onclick scroll functionality.
        $(scroll_child).on('click', function() {
            window.cae_functions['selectScroll__toggleSelected'](this);
        });

        // Attach to parent.
        $(scroll_nav).append(scroll_child);

        // Create scroll content element.
        $(this).data('name', scroll_name_array.pop());
        $(this).appendTo(scroll_content);

        // Automatically display first tab by default.
        if (first_scroll) {
            $(scroll_child).addClass('selected');
            $(this).addClass('selected');
        }
        first_scroll = false;
    });

    // Put SelectScroll elements back into dom.
    $(scroll_nav).appendTo($(this));
    $(scroll_content).appendTo($(this));

});


/**
 * Handles selection scroll click events.
 */
window.cae_functions['selectScroll__toggleSelected'] = function(selected_scroll) {
    // Remove 'selected' class from all selectscroll-nav siblings and apply to self.
    $(selected_scroll).siblings('.selected').removeClass('selected');
    $(selected_scroll).addClass('selected');

    // Toggle scroll-content styles to show/hide.
    let scroll_content = $(selected_scroll).parent().parent().children('.selectscroll-content');
    $(scroll_content).children().each(function() {
        $(this).removeClass('selected');

        if ($(this).data('name') == $(selected_scroll).text()) {
            $(this).addClass('selected');
        }
    });
}
