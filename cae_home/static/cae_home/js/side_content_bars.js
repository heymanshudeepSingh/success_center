/**
 *  Handles displaying and removal of side content bars.
 *
 *  Note that content bars default to hidden. That way, if JS is broken, they simply don't show.
 *  This also prevents visual bug of content bars displaying for half a second on page load,
 *  before JS can process.
 */


// Wait for full page load.
$(document).ready(function() {
    // console.log('Started side_content_bars.js file.');

    // Check if content bars have any elements. Remove if not. Hide if they do.
    if ($('#content-bar-left .bar-content').children().length == 0) {
        $('#content-bar-left').remove();
    } else {
        $('#content-bar-left').removeClass('hidden');
        hide_left_bar();
    }
    if ($('#content-bar-right .bar-content').children().length == 0) {
        $('#content-bar-right').remove();
    } else {
        $('#content-bar-right').removeClass('hidden');
        hide_right_bar();
    }

    // Handle menu clicks.
    // Hide left bar on left arrow click.
    $('#content-bar-left .arrow-left').on('click', function() {
        // console.log('Clicked left arrow.');
        hide_left_bar();
    });
    // Show left bar on right arrow click.
    $('#content-bar-left .arrow-right').on('click', function() {
        // console.log('Clicked right arrow.');
        show_left_bar()
    });
    // Hide right bar on right arrow click.
    $('#content-bar-right .arrow-right').on('click', function() {
        // console.log('Clicked left arrow.');
        hide_right_bar();
    });
    // Show right bar on left arrow click.
    $('#content-bar-right .arrow-left').on('click', function() {
        // console.log('Clicked right arrow.');
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
