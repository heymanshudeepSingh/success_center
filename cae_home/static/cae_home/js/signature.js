/**
 *  General logic for the signature-form field.
 */


/**
 *  Create function with JQuery-esque syntax.
 *  IE: Call with:
 *      $(element).signatureFormField()
 */
(function( $ ) {

    // Function call name for base "Signature Form" widget.
    $.fn.signatureField = function() {

        // Go through each element with function.
        // Filter out anything that isn't a signature form field.
        this.filter('.form-widget-signature-field').each(function() {
            createSignatureFormWidget(this);
        });

        // Allow other functions to chain off element, if desired.
        return this;

    };

}( jQuery ));


/**
 * Function to create specialized form widget.
 *  :signature_element: The widget element to manipulate.
 */
function createSignatureFormWidget(signature_element) {

    // Get elements.
    var signature_parent = $(signature_element).parent().parent();
    var parent_form = $(signature_parent).parent().parent();
    var widget_field_error = $(signature_parent).prev();
    var signature_data = $(signature_element).attr('value');

    // Verify field error exists.
    if (!($(widget_field_error).is('div') && $(widget_field_error).attr('class', 'alert error'))) {
        widget_field_error = null;
    }

    // console.log('signature_element:');
    // console.log(signature_element);
    // console.log('sig_parent:');
    // console.log(signature_parent);
    // console.log('parent_form:');
    // console.log(parent_form);
    // console.log('widget_field_error');
    // console.log(widget_field_error);
    // console.log('signature_data:');
    // console.log(signature_data);

    // Temporarily remove all elements from widget space.
    $(signature_parent).children().each(function () {
        $(this).detach();
    });

    // Create widget elements.
    var signature_widget = $('<fieldset class="signature-widget"></fieldset>');
    var widget_legend = $('<legend><h4>Signature</h4></legend>');
    var widget_signature_pad = $('<canvas class="signature-pad" width="500px" height="150px"></canvas>');
    var widget_signature_pad_container = $('<div class="signature-wrapper"></div>');
    var widget_clear = $('<button class="signature-widget-clear secondary">Clear</button>');
    var widget_input = signature_element;
    $(widget_input).hide();

    // Combine and readd widget elements.
    if ($(widget_field_error) != null) {
        $(widget_field_error).detach();
        $(widget_field_error).appendTo(signature_widget);
    }
    $(widget_legend).appendTo(signature_widget);
    $(widget_signature_pad).appendTo(widget_signature_pad_container);
    $(widget_signature_pad_container).appendTo(signature_widget);
    $(widget_clear).appendTo(signature_widget);
    $(widget_input).appendTo(signature_widget);
    $(signature_parent).append(signature_widget);

    // Load 3rd Party signature element into canvas widget.
    var signature_pad = new SignaturePad($(widget_signature_pad).get(0), {});

    // Populated form data, if provided.
    if (typeof signature_data !== typeof undefined && signature_data !== false) {
        signature_pad.fromDataURL(signature_data);
    }

    // Find form's "submit" button and add event listener.
    var form_submit = null;
    $(parent_form).children().each(function () {

        // Examine each direct grandchild.
        $(this).children().each(function () {

            // Check for submit button.
            if ( $(this).is('input') && $(this).attr('type') == 'submit' ) {
                form_submit = $(this);
            }

        });

    });

    // Raise error if failed to find submit button.
    if (form_submit == null) {
        throw new Error('Failed to locate form submit button. Signature widget data unable to submit.');
    }

    // Add event listener to clear button.
    $(widget_clear).get(0).addEventListener('click', function(event) {
        event.preventDefault();
        signature_pad.clear();
    });

    // Add event listener to submit button.
    $(form_submit).get(0).addEventListener('click', function(event) {
        var dataUrl = signature_pad.toDataURL('image/png');
        $(widget_input).attr('value', dataUrl);
    });
}


/**
 * Handle for signature change.
 # I'm not sure if this was doing anything?
 */
function formSignatureOnChange() {
    // var mycanvas = document.getElementById("signature"); //get your canvas
    // var image = mycanvas.toDataURL(); //Convert
    // var image_arr = image.split(',')
    document.getElementById('form-signature-input').value = image_arr[1];
}


/**
 * Detects and initializs html emements with the signature widget class.
 */
$(document).ready(function() {
    // Generate form widgets on page load.
    $('.form-widget-signature-field').signatureField();
});
