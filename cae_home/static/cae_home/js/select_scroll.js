/**
 * Logic for SelectScroll custom CSS element.
 * Behaves somewhat similarly to TabbedPanel element.
 */

// console.log('Loaded select_scroll.js');


// Iterate through each SelectScroll element found on page.
$('div.select-scroll').each(function() {

    // Save and detach root element children.
    let scroll_root = $(this);
    let root_children = $(this).children('div').detach();

    // Initialize selection elements.
    let first_scroll = true;
    let scroll_name_array = [];
    let scroll_nav_container = $('<div class="selectscroll-nav-container"></div>')
    let scroll_nav = $('<ul class="selectscroll-nav"></ul>');
    let scroll_content = $('<div class="selectscroll-content"></div>');

    // Add scroll buttons to nav element.
    let scroll_button_left = $('<div class="arrow arrow-left"><i class="fa fa-chevron-circle-left"></i></div>');
    let scroll_button_right = $('<div class="arrow arrow-right"><i class="fa fa-chevron-circle-right"></i></div>');
    $(scroll_nav_container).append(scroll_button_left);
    $(scroll_nav_container).append(scroll_button_right);

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
    $(scroll_nav_container).appendTo($(this));
    $(scroll_nav).appendTo(scroll_nav_container);
    $(scroll_content).appendTo($(this));

    // Add button click functionality.
    // Save variables to element "data" to ensure no dumb variable scope problems,
    // if multiple instances of this SelectScroll element exist on page.
    // Note that .width() does not seem to take element borders into account, so we
    // have to manually add those too (will break if we ever change css border size).
    let parent_width = $(scroll_nav_container).width() - 58;
    let scroll_item_count = $(scroll_nav).children('li').length;
    let scroll_item_width = $(scroll_nav).children('li').first().width() + 2;
    let scroll_width = scroll_item_width * scroll_item_count;
    // console.log();
    // console.log();
    // console.log('scroll_item_width: ' + scroll_item_width);
    // console.log('scroll_item_count: ' + scroll_item_count);
    // console.log('parent_width: ' + parent_width);
    // console.log('scroll_width: ' + scroll_width);
    $(scroll_nav).data('visible_size', parent_width);
    $(scroll_nav).data('curr_scroll_position_left', 0);
    $(scroll_nav).data('curr_scroll_position_right', parent_width);
    $(scroll_nav).data('scroll_max', scroll_width);

    $(scroll_button_left).on("click", function() {
        console.log();
        console.log();
        console.log('clicked left');

        // Calculate amount to scroll.
        let curr_position_left = $(scroll_nav).data('curr_scroll_position_left')
        let curr_position_right = $(scroll_nav).data('curr_scroll_position_right')
        // console.log('curr_position_left: ' + curr_position_left);
        // console.log('curr_position_right: ' + curr_position_right);
        // console.log('scroll_max: ' + 0);

        let move_amount = 300
        if ( (curr_position_left - move_amount) <= 0 ) {
            // Would match or go past end. Recalculate so we only scroll until we hit max.
            move_amount = curr_position_left;
        }

        // Scroll calculated amount.
        // First update data positions.
        $(scroll_nav).data('curr_scroll_position_left', curr_position_left - move_amount);
        $(scroll_nav).data('curr_scroll_position_right', curr_position_right - move_amount);
        // Then loop through each li child ScrollBox item and move.
        // We do this so that the outer nav can have "overflow: hidden" and cause these
        // li children to still be hidden when they scroll out of view.
        $(scroll_nav).children('li').each(function() {
            $(this).animate({'left': '+=' + move_amount + 'px'});
        });
    });
    $(scroll_button_right).on("click", function() {
        console.log();
        console.log();
        console.log('clicked right');

        // Calculate amount to scroll.
        let curr_position_left = $(scroll_nav).data('curr_scroll_position_left')
        let curr_position_right = $(scroll_nav).data('curr_scroll_position_right')
        // console.log('curr_position_left: ' + curr_position_left);
        // console.log('curr_position_right: ' + curr_position_right);
        // console.log('scroll_max: ' + $(scroll_nav).data('scroll_max'));

        let move_amount = 300
        if ( (curr_position_right + move_amount) >= $(scroll_nav).data('scroll_max') ) {
            // Would match or go past end. Recalculate so we only scroll until we hit max.
            move_amount = $(scroll_nav).data('scroll_max') - curr_position_right;
        }

        // Scroll calculated amount.
        // First update data positions.
        $(scroll_nav).data('curr_scroll_position_left', curr_position_left + move_amount);
        $(scroll_nav).data('curr_scroll_position_right', curr_position_right + move_amount);
        // Then loop through each li child ScrollBox item and move.
        // We do this so that the outer nav can have "overflow: hidden" and cause these
        // li children to still be hidden when they scroll out of view.
        $(scroll_nav).children('li').each(function() {
            $(this).animate({'left': '-=' + move_amount + 'px'});
        });
    });

});


/**
 * Handles selection scroll click events.
 */
window.cae_functions['selectScroll__toggleSelected'] = function(selected_scroll) {

    // Remove 'selected' class from all selectscroll-nav siblings and apply to self.
    $(selected_scroll).siblings('.selected').removeClass('selected');
    $(selected_scroll).addClass('selected');

    // Toggle scroll-content styles to show/hide.
    let scroll_content = $(selected_scroll).parent().parent().parent().children('.selectscroll-content');
    $(scroll_content).children().each(function() {
        $(this).removeClass('selected');

        if ($(this).data('name') == $(selected_scroll).text()) {
            $(this).addClass('selected');
        }
    });
}
