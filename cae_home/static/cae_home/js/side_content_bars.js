/**
 *  Handles fadeout and removal of status messages.
 */


// Wait for full page load.
$(document).ready(function() {
    console.log('Started side_content_bars.js file.');

    var left_bar = $('#content-bar-left');
    var right_bar = $('#content-bar-right');
    console.log(left_bar);
    console.log(right_bar);

    // Check if content bars have any elements. Hide if not.
    if (left_bar.children().length == 0) {
        left_bar.remove();
    }
    if (right_bar.children().length == 0) {
        right_bar.remove();
    }

    // Loop through right bar.
    let right_header_array = [];
    let right_content_dict = {}
    let right_children = right_bar.children();
    let dict_key = 'no_header';
    let dict_value = null;

    for (let index = 0; index < right_children.length; index++) {
        // console.log(right_children[index]);

        if ($(right_children[index]).is('h2') || $(right_children[index]).is('h3')) {
            // console.log('Is header.');
            // Add content to previous dict entry.
            if (dict_value != null) {
                right_content_dict[dict_key] = dict_value;
            }

            // Get new header.
            dict_key = $(right_children[index]).prop('outerHTML');
            dict_value = null;
            right_header_array.push($(right_children[index]).detach());
        } else {
            if (dict_value == null) {
                dict_value = $(right_children[index]).detach();
            } else {
                dict_value += $(right_children[index]).detach();
            }
        }
    }

    // Add final content values to lst dict entry.
    if (dict_value != null) {
        right_content_dict[dict_key] = dict_value;
    }

    // console.log('Header array:');
    // console.log(right_header_array);
    // console.log('Header Dict:');
    // console.log(right_content_dict);

    // console.log('============================================================');
    // console.log('============================================================');

    let append_header = $('<div class="content-bar-header"></div>');
    for (let index = 0; index < right_header_array.length; index++) {

        let header_wrapper = $('<div class=content-bar-header-wrapper></div>');
        header_wrapper.append(right_header_array[index][0]);
        append_header.append(header_wrapper);

        // append_header.append(right_header_array[index][0]);
    }

    // console.log(right_bar_header);
    right_bar.append(append_header);
    right_bar.append('<div class="content-bar-content">Content</div>');

    let right_bar_header = $('.content-bar-header').children();

    console.log(right_bar_header);
    console.log('============================================================');
    console.log('============================================================');
    for (let index = 0; index < right_bar_header.length; index++) {

        // let width_holder = $(right_bar_header[index]).width();
        // $(right_bar_header[index]).width($(right_bar_header[index]).height());
        // $(right_bar_header[index]).height(width_holder);

        // console.log($(right_bar_header[index]).children().width());

        let child_width = $(right_bar_header[index]).children().width();
        let child_height = $(right_bar_header[index]).children().height();
        console.log('Width: ' + child_width);
        console.log('Height: ' + child_height);

        // $(right_bar_header[index]).css('max-height', child_height);
        // $(right_bar_header[index]).css('max-width', child_width);

        $(right_bar_header[index]).css('height', child_width);
        $(right_bar_header[index]).css('width', child_height);
        // $(right_bar_header[index]).css('padding-top', child_width);
        // $(right_bar_header[index]).css('max-height', child_width);
        // $(right_bar_header[index]).css('max-width', child_height);

        $(right_bar_header[index]).children().css('width', child_width);
        // $(right_bar_header[index]).children().css('height', child_width);
        // $(right_bar_header[index]).children().css('max-width', old_height);
        // $(right_bar_header[index]).children().css('max-height', old_width);
        console.log(right_bar_header[index]);

    }
});
