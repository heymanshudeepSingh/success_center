/**
 *  General logic for the selectbuttons form widget.
 */


/**
 *  Create function with JQuery-esque syntax.
 *  IE: Call with:
 *      $(element).selectButtons()
 */
(function( $ ) {

    // Function call name.
    $.fn.selectButtons = function() {

        // Go through each element with function.
        // Filter out anything that isn't a select form field.
        this.filter("select").each(function() {
            createSelectButtonWidget(this);
        });

        // Allow other functions to chain off element, if desired.
        return this;

    };

}( jQuery ));


/**
 * Function to create specialized form widget.
 */
function createSelectButtonWidget(select_element) {

    // Parse select element to create selection_list.
    var selection_list = [];
    $(select_element).children().each(function() {
        child_value = this['value'];
        child_data = this['childNodes'][0]['data'];

        // Ignore placeholder item.
        if (child_data != '---------') {
            selection_list.push({
                'pk': child_value,
                'text': child_data,
            });
        }
    });

    // Now create new widget with selection_list data.
    button_widget = $('<div class="select-buttons"></div>');
    $(selection_list).each(function() {
        button_instance = $('<div class="select-item"><p>' + this['text'] + '</p></div>');
        button_instance.data('id', this['pk']);
        button_widget.append(button_instance);
    });

    // Add elements to dom and add click function handling.
    $(select_element).addClass('accessibility-element');
    $(select_element).parent().append(button_widget);
    $('form .select-buttons .select-item').on('click', function() {
        toggleSelectbutton(this);
    });
}


/**
 * Toggles selection class to make selection obvious to user.
 */
function toggleSelectbutton(selected_button) {
    console.log('Clicked button');
    // console.log(selected_button);

    // First remove selected class from sibling elements.
    $(selected_button).siblings().each(function() {
        // Check if sibling has class.
        if ($(this).hasClass('selected')) {
            // Remove class.
            $(this).removeClass('selected');
        }
    });

    // Add selected class to clicked button.
    $(selected_button).addClass('selected');

    // Save selected id to original input element.
    parent_element = $(selected_button).parent().siblings('.accessibility-element')[0];
    $(parent_element).val($(selected_button).data('id'));
}


/**
 * Detects and initializs html emements with the selectbuttons class.
 */
$(document).ready(function() {

    $('.form-widget-select-buttons').selectButtons();
});
