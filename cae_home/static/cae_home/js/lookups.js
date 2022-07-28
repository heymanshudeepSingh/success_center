/**
 * Handles API lookup functionality.
 */


/**
 * Function to make api call, passing provided identifier to WmuUser model API lookup view.
 */
window.cae_functions['api_lookup__wmu_user'] = function(identifier) {

    console.log('\n\n\n\n');
    console.log('API Lookup: WmuUser');

    // Make AJAX call to lookup model data.
    $.ajax({
        url: '/cae_tools/api/wmu_user/',
        type: 'GET',
        data: {'identifier': identifier},
        success: function(result) {

            // Parse desired value from returned menu options.
            result_id = result['id'];
            result_bronco = result['bronco_net'];
            result_winno = result['winno'];
            result_first = result['first_name'];
            result_last = result['last_name'];

            console.log('result:');
            console.log(result);

            // Update datalist corresponding to search box.
            let datalist_options = '';

            // Proceed if result had 1 or more values.
            if (result_id != null) {
                datalist_options = '<option value="' + result_bronco + '">'
                + result_bronco + ' / ' + result_winno + ' - ' + result_first + ' ' + result_last
                + '</option>';
            }

            // Set html datalist to parsed options.
            console.log('\n\nuser_id_datalist:');
            console.log($('#user_id_datalist'));
            console.log('inner_html:');
            console.log($('#user_id_datalist').html());
            console.log('\ndatalist_options:');
            console.log(datalist_options);
            $('#user_id_datalist').html(datalist_options);
        },

        error: function(xhr, status, error) {
            console.log(xhr);
            console.log(status);
            console.log(error);
        },

    });

}


// Wait for full page load.
$(document).ready(function() {
    /**
     * Written in end of summer 2022.
     *
     * This was the initial attempt at the "allow users to enter any arbitrary BroncoNet/Winno into a form field,
     * and then dynamically grow the field choices in real time, if the value corresponded to a real user".
     * However, Chris said that would potentially ping main campus LDAP too frequently so we can't use it.
     * We found a work-around. But for now, this original logic is kept for reference, in case it's somehow helpful
     * in the future.
     *
     *
     *
     * To explain the logic, basically the this idea was that the form:
     *  * Would use a standard text field.
     *  * This text field would have a datalist associated with it. In this case, we gave it the HTML id of
     *    "#user_id_datalist". A datalist simulates a ChoiceField by showing options the user can select from.
     *  * On any keypress into this field, it would send the current input as an api call. That's what this section
     *    of code is doing.
     *  * The API would do the "heavy lifting" of actually querying the Django database for a corresponding model. If
     *    not found, then it would query LDAP using the cae_home/utils helper functions. If a corresponding user was
     *    located, then the api would return data about that user, to parse with JavaScript and add as a new value in
     *    the original form field datalist.
     *  * A problem is that this resulted in very ugly front-end visual display. But it technically worked.
     *  * We started experimenting with using a select2 field instead of a standard text field, because select2 is
     *    more dynamic and could potentially make the front-end display better. But that's when Chris gave the news
     *    that we can't use this logic at all, rip.
     *
     *
     *
     * To test adding this logic back in, create a form with the following values:
     * In form __init__()
     *      # Set datalist value, for auto-completion.
     *      self.fields['user_id'].widget.attrs['list'] = 'user_id_datalist'
     *
     * At form root
     *      class Media:
     *          # Additional JS file definitions.
     *          js = ('cae_home/js/lookups.js',)
     *
     * Note that the form should also have a field of "user_id".
     * Once the above is added to a form, uncomment out the below JS code, and it should hopefully work.
     */

//    console.log('doc is ready!');
//
//    var ele = $('#id_user_id');
//    console.log(ele);
//
//    // Call lookup logic on keyboard input into form field.
//    $('#id_user_id').on('input', function(event) {
//        console.log('event:');
//        console.log(event);
//        console.log(event.target.value);
//        window.cae_functions['api_lookup__wmu_user'](event.target.value);
//    });

});
