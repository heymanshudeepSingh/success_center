/**
 * Detects and initializes tabbed panel elements.
 */

// console.log('Loaded tabbed_panel.js');


$('.panel.tabs').each(function() {

    // Save panel body element.
    var panel_body = $(this).children('.body, .content');

    // Detach all tab elements inside body.
    var tabs = $(panel_body).children('.tab').detach();

    // Create tab elements.
    var first_tab = true;
    var tab_name_array = [];
    var tab_nav = $('<ul class="tab-nav"></ul>');
    var tab_content = $('<div class="tab-content"></div>');

    $(tabs).each(function() {

        // Create tab navigation element.
        var header = $(this).children(':header:first()').detach();
        var tab_child = $('<li></li>').append(header);
        tab_name_array.push($(header).text());

        // Set onclick tab functionality.
        $(tab_child).on('click', function() {
            toggleSelectedPanelTab(this);
        });

        // Attach to parent.
        $(tab_nav).append(tab_child);


        // Create tab content element.
        $(this).data('name', tab_name_array.pop());
        $(this).appendTo(tab_content);


        // Automatically display first tab by default.
        if (first_tab) {
            $(tab_child).addClass('selected');
            $(this).addClass('selected');
        }
        first_tab = false;
    });

    // Put tab elements back into dom.
    $(tab_nav).appendTo(panel_body);
    $(tab_content).appendTo(panel_body);
});


/**
 * Handles tab click events.
 */
function toggleSelectedPanelTab(selected_tab) {

    // Remove 'selected' class from all tab-nav siblings and apply to self.
    $(selected_tab).siblings('.selected').removeClass('selected');
    $(selected_tab).addClass('selected');

    // Toggle tab-content styles to show/hide.
    var tab_content = $(selected_tab).parent().parent().children('.tab-content');
    $(tab_content).children().each(function() {
        $(this).removeClass('selected');

        if ($(this).data('name') == $(selected_tab).text()) {
            $(this).addClass('selected');
        }
    });
}
