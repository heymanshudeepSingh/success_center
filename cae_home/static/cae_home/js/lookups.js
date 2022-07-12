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
            result_id = result['bronco_net'];
            result_first = result['first_name'];
            result_last = result['last_name'];

            console.log('result:');
            console.log(result);

            // Update datalist corresponding to search box.
            let datalist_options = '';

            // Proceed if result had 1 or more values.
            if (result_id != null) {
                datalist_options = '<option value="' + result_id + '">' + result_id + ' - ' + result_first + ' ' + result_last + '</option>';
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

    // Call lookup logic on keyboard input into form field.
    $('#id_user_id').on('input', function(event) {
        console.log('event:');
        console.log(event);
        console.log(event.target.value);
        window.cae_functions['api_lookup__wmu_user'](event.target.value);
    });
});
