/**
 *  Handles removal of empty content bars.
 */


// Wait for full page load.
$(document).ready(function() {
    console.log('Started side_content_bars.js file.');

    var left_bar = $('#content-bar-left');
    var right_bar = $('#content-bar-right');
    console.log(left_bar);
    console.log(right_bar);

    // Check if content bars have any elements. Remove if not. Hide if they do.
    if (left_bar.children().length == 0) {
        left_bar.remove();
    } else {
        hide_left_bar();
    }
    if (right_bar.children().length == 0) {
        right_bar.remove();
    } else {
        hide_right_bar();
    }

    // Handle menu clicks.
    // Hide left bar on left arrow click.
    $('#content-bar-left .arrow-left').on('click', function() {
        console.log('Clicked left arrow.');
        hide_left_bar();
    });
    // Show left bar on right arrow click.
    $('#content-bar-left .arrow-right').on('click', function() {
        console.log('Clicked right arrow.');
        show_left_bar()
    });
    // Hide right bar on right arrow click.
    $('#content-bar-right .arrow-right').on('click', function() {
        console.log('Clicked left arrow.');
        hide_right_bar();
    });
    // Show right bar on left arrow click.
    $('#content-bar-right .arrow-left').on('click', function() {
        console.log('Clicked right arrow.');
        show_right_bar()
    });


    /**
     * Hide left bar.
     */
    function hide_left_bar() {
        $('#content-bar-left .bar-content').addClass('hidden');
        $('#content-bar-left .arrow-right').removeClass('hidden');
        $('#content-bar-left .arrow-left').addClass('hidden');
    }

    /**
     * Display left bar.
     */
    function show_left_bar() {
        $('#content-bar-left .bar-content').removeClass('hidden');
        $('#content-bar-left .arrow-right').addClass('hidden');
        $('#content-bar-left .arrow-left').removeClass('hidden');
    }

    /**
     * Hide right bar.
     */
    function hide_right_bar() {
        $('#content-bar-right .bar-content').addClass('hidden');
        $('#content-bar-right .arrow-left').removeClass('hidden');
        $('#content-bar-right .arrow-right').addClass('hidden');
    }

    /**
     *  Display right bar.
     */
    function show_right_bar() {
        $('#content-bar-right .bar-content').removeClass('hidden');
        $('#content-bar-right .arrow-left').addClass('hidden');
        $('#content-bar-right .arrow-right').removeClass('hidden');
    }

});
