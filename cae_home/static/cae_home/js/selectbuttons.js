/**
 *  General logic for the selectbuttons form widget.
 */


/**
 *  Create function with JQuery-esque syntax.
 *  IE: Call with either:
 *      $(element).selectButtons()
  *      $(element).selectButtonsSide()
 */
(function( $ ) {

    // Function call name for base "SelectButtons" widget.
    $.fn.selectButtons = function() {

        // Go through each element with function.
        // Filter out anything that isn't a select form field.
        this.filter("select").each(function() {
            createSelectButtonWidget(this);
        });

        // Allow other functions to chain off element, if desired.
        return this;

    };

    // Function call name for "SelectButtonsSide" widget.
    $.fn.selectButtonsSide = function() {

        // Go through each element with function.
        // Filter out anything that isn't a select form field.
        this.filter("select").each(function() {
            createSelectButtonWidget(this, true);
        });

        // Allow other functions to chain off element, if desired.
        return this;

    };

}( jQuery ));


/**
 * Function to create specialized form widget.
 *  :select_element: The widget element to manipulate.
 *  :display_side: Boolean to determine if widget should be rendered on side.
 */
function createSelectButtonWidget(select_element, display_side=false) {

    // If widget is meant to display on side, we need to move element within form.
    if (display_side) {

        // Get parent form.
        var parent_container = $(select_element).parent().parent().parent();

        // Add css class to form to handle columns.
        $(parent_container).addClass('multi-col');

        // Get widget to move and add it to a seperate sub-div.
        var right_form_inputs = $('<div class="form-col mobile-display-first"></div>');
        var full_widget = $(select_element).parent().parent();
        $(full_widget).appendTo(right_form_inputs);

        // Move all remaining children in form to sub-div.
        var left_form_inputs = $('<div class="form-col"></div>');
        $(parent_container).children().each(function() {
            $(this).appendTo(left_form_inputs);
        });

        // Now reattach both left and right form sub-divs.
        $(left_form_inputs).appendTo(parent_container);
        $(right_form_inputs).appendTo(parent_container);
    }


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
    $('.form-widget-select-buttons-side').selectButtonsSide();
});
