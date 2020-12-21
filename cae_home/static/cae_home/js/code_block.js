/**
 *  General logic for the code block css/html element.
 */


/**
 *  Create function with JQuery-esque syntax.
 *  IE: Call with either:
 *      $(element).code_block()
 */
(function( $ ) {

    // Function call name for base "Code Block" element.
    $.fn.code_block = function() {

        this.each(function() {
            formatCodeBlockElement(this);
        });

        // Allow other functions to chain off element, if desired.
        return this;

    };

}( jQuery ));


/**
 * Function to format code block html/css element.
 *  :code_container: The element to manipulate.
 */
function formatCodeBlockElement(code_container) {

    let pre_element, code_element, inner_element_html;

    // Search for existing elements in code block.
    if ( $(code_container).is('pre') ) {
        // Container is "pre" element.
        pre_element = code_container;

    } else if ( $(code_container).is('code') ) {
        // Container is "code" element.
        code_element = code_container;

    } else {
        // Container is not "pre" or "code" elements. Check direct child.
        if ( $(code_container).has('pre')['length'] > 0 ) {
            // Direct "pre" element found.
            pre_element = $(code_container).children('pre')[0];

            // Check for inner code element.
            if ( $(pre_element).has('code')['length'] > 0 ) {
                code_element = $(pre_element).children('code')[0];
            }

        } else if ( $(code_container).has('code')['length'] > 0 ) {
            // Direct "code" element found.
            code_element = $(code_container).children('code')[0];

        } else {
            // Neither "pre" or "code" direct elements found. Do nothing for now.
            // console.log('Failed to find "<pre>" or "code" elements in code block.');
        }

    }


    // Handle based on found existing elements.
    if (pre_element == null && code_element == null) {
        // Neither "pre" or "code" elements were present. Create both.

        inner_element_html = $(code_container).html();
        $(code_container).empty();
        code_element = $('<code></code>')
        $(code_element).append(inner_element_html);
        pre_element = $('<pre></pre>');
        $(pre_element).append(code_element);
        $(code_container).append(pre_element);

        // Standardize code element spacing, using "pre" element.
        resetCodeTabbing(pre_element);

        // Escaped characters seem to be fine in this case so do nothing further.

    } else if (pre_element != null && code_element == null) {
        // Only "pre" element was found. Create "code" element.

        inner_element_html = $(pre_element).html();
        $(pre_element).empty();
        code_element = document.createElement('code');
        code_element.append('\n' + inner_element_html);
        pre_element.append(code_element);

        // Standardize code element spacing, using "pre" element.
        resetCodeTabbing(pre_element);

        // For some reason, escaped characters will not display properly here. Correct this with "pre" element.
        correctCodeEscapedChars(pre_element);

    } else if (pre_element == null && code_element != null) {
        // Only "code" element was found. Create "pre" element.

        inner_element_html = $(code_element).html();
        $(code_container).empty();
        pre_element = document.createElement('pre');
        pre_element.append(inner_element_html);
        code_container.append(pre_element);

        // Standardize code element spacing, using "pre" element.
        resetCodeTabbing(pre_element);

        // For some reason, escaped characters will not display properly here. Correct this with "pre" element.
        correctCodeEscapedChars(pre_element);

        // Finally, do one more step to correct top spacing.
        inner_element_html = $(pre_element).html();
        $(pre_element).empty();
        $(pre_element).append('\n' + inner_element_html);

    } else {
        // Both "pre" and "code" elements exist. Nothing to create.

        // Standardize code element spacing, using "pre" element.
        resetCodeTabbing(pre_element);

        // Escaped characters seem to be fine in this case so do nothing further.
    }

    // Style elements, now that they're formatted consistently.
    // Check for expected classes.
    if (! $(pre_element).hasClass('highlight') ) {
        $(pre_element).addClass('highlight');
    }
    if (! $(pre_element).hasClass('code') ) {
        $(pre_element).addClass('code');
    }
}


/**
 * Replace extra spacing at start of code blocks.
 * This makes it so it doesn't matter where our code elements are nested within our template code.
 */
function resetCodeTabbing(reset_element) {
    let html = $(reset_element).html();
    let pattern = html.match(/\s*\n[\t\s]*/);
    $(reset_element).html(html.replace(new RegExp(pattern, "g"),'\n'));
}


/**
 * Handle for escaped characters, such as the "<" sign being typed as "&lt;".
 * This makes it so the intended characters will always display, instead of the escaped versions.
 */
function correctCodeEscapedChars(escaped_element) {
    let escaped_element_html = $(escaped_element).html();
    $(escaped_element).empty();
    $(escaped_element).append(htmlDecode(escaped_element_html));
}


/**
 * Ensures syntax is displayed properly and consistently.
 *
 * From https://stackoverflow.com/a/34064434
 */
function htmlDecode(html_input) {
  let doc = new DOMParser().parseFromString(html_input, "text/html");
  return doc.documentElement.textContent;
}


$(document).ready(function() {
    $('.code-block').code_block();
});
