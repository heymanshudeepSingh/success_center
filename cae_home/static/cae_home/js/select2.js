/**
 * Detects and initializes html elements with the select2 class.
 *
 * For "matcher" logic, see https://stackoverflow.com/questions/31019609/filter-by-id-as-well-as-text-in-select2
 */


/**
 * Custom function to modify default matching.
 */
window.cae_functions['select2__match_custom'] = function(params, data) {
    // If there are no search terms, return all of the data
    if ($.trim(params.term) === '') {
      return data;
    }

    // Do not display the item if there is no 'text' property.
    if (typeof data.text === 'undefined') {
      return null;
    }

    // Search by value.
    if (data.text.indexOf(params.term) > -1) {
      return data;
    }

    // Search by id.
    if (data.id.indexOf(params.term) > -1) {
      return data;
    }

    // Return `null` if the term should not be displayed
    return null;
}


$(document).ready(function() {

    // Basic select2 form element.
    $('.form-widget-select2').select2({
        matcher: window.cae_functions['select2__match_custom'],
    });

    // Basic select2 form element, but with ability for user to create new entries in real time.
    $('.form-widget-select2-with-tagging').select2({
        tags: true,
        selectOnClose: true,
        matcher: window.cae_functions['select2__match_custom'],
    });

    // Multi-choice select2 form element.
    $('.form-widget-select2-multiple').select2({
        matcher: window.cae_functions['select2__match_custom'],
    });

    /**
     * General logic to allow proper tabbing/focus behavior, when a user tries to tab to "next form field" on a form.
     * See https://stackoverflow.com/a/49261426 for source + explanation.
     */
    // On first focus (bubbles up to document), open the menu.
    $(document).on('focus', '.select2-selection.select2-selection--single', function (e) {
      $(this).closest(".select2-container").siblings('select:enabled').select2('open');
    });

    // Steal focus during close - only capture once and stop propogation.
    $('select.select2').on('select2:closing', function (e) {
      $(e.target).data("select2").$selection.one('focus focusin', function (e) {
        e.stopPropagation();
      });
    });
});
