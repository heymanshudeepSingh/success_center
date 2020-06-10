
/**
 * JavaScript Logic for custom "page tabbing" CSS elements.
 *
 * By default, it will create tabs for all H2 element direct children.
 */


// Global Variables.
var pagetabs_header_dict = {
    "All": [],
    "Other": [],
};
var allow_all_headers = true;
var pagetabs_header_ordering = [];
var generate_page_tab_bool = true;

// Get "tabbable topics" if provided.
var page_tabbable_topics = []
if (document.getElementById("pagetabs-template-variables")) {
    // Topics were provided by template.
    page_tabbable_topics = document.getElementById("pagetabs-template-variables").innerHTML;

    // Topics acquired. Element no longer servers a purpose. Remove.
    document.getElementById("pagetabs-template-variables").remove();
} else {
    // Topics were not provided by template.
    page_tabbable_topics =["Test 1", "Test 2", "Test 3"];
}


/**
 * The start of page tabbing logic.
 */
function page_tab_generation_main() {
    // Get default pagetab content container.
    var pagetab_content_containers = document.getElementsByClassName("page-tabs");

    // Handle for each pagetab container found on page. This allows multiple to exist on a page, if desired.
    for (var index = 0; index < pagetab_content_containers.length; index++) {
        // Populate variables.
        pagetabs_header_dict = {
            "All": [],
            "Other": [],
        };
        pagetabs_header_ordering = [];
        populate_page_tab_variables(pagetab_content_containers[index]);
        generate_page_tabs(pagetab_content_containers[index], index);
    }
}


/**
 * Loops through all page content elements. All elements are automatically stored into header_dict["all"].
 *
 * If element is a H2 header, then a new key is created in header_dict, using the H2 text value.
 *
 * If at least one H2 header has been found, then the element is stored under both header_dict["all"] and
 * header_dict[<header_name>], where <header_name> is the most recently found H2 element.
 */
function populate_page_tab_variables(pagetab_content_container) {
    var current_header = "Other";

    // Loop through all child content elements.
    var page_length = pagetab_content_container.childNodes.length;
    for (var index = 0; index < page_length; index++) {
        // Save current element for easy reference.
        var current_element = pagetab_content_container.childNodes[index];

        // Check if element is empty. We can skip these.
        if (current_element.nodeName == "#text" && current_element.data.trim() == "") {
            // Pass. Is empty element. We probably don't want to include this.

        // Proceed if element has content.
        } else {
            // Check if element is H2 header. If so, create a new key in header_dict, using element's text value.
            if (current_element.tagName == "H2") {
                current_header = current_element.firstChild.nodeValue;

                // Check if item is in "tabbable topics" array. By default, all headers are allowed.
                if (allow_all_headers || page_tabbable_topics.includes(current_header)) {
                    // Item is in "tabbable topics" array. We can create a new page tab for this content.
                    // Create new key with header value, and also push to ordering dict to preserve page content ordering.
                    pagetabs_header_dict[current_header] = [];
                    pagetabs_header_ordering.push(current_header);
                } else {
                    // Item is not in "tabbable topics" array. Put content into "Other" tab.
                    current_header = "Other";
                }
            }

            // Add element into "all" key.
            pagetabs_header_dict["All"].push(pagetab_content_container.childNodes[index].cloneNode(true));
            // Also add element to dictionary, under current found header.
            pagetabs_header_dict[current_header].push(pagetab_content_container.childNodes[index]);
        }
    }

    // Check if any elements were added to "Other" section. If so, add "Other" to list of dict values.
    if (pagetabs_header_dict["Other"].length > 0) {
        pagetabs_header_ordering.push("Other");
    }
}


/**
 * Generates actual tab navigation elements on page.
 */
function generate_page_tabs(pagetab_content_container, element_num) {

    // Check if we have at least two unique headers to create tabs for.
    // If so, generate pagetabs html. Otherwise, leave page as is.
    header_array_clone = pagetabs_header_ordering.slice();

    // We don't want to count the "Other" tab for counting purposes. It may or may not be present.
    if (header_array_clone.includes("Other")) {
        var index = header_array_clone.indexOf("Other");
        header_array_clone.splice(index, 1);
    }

    // Now that we have an array of only "unique" tab values, check length.
    if (header_array_clone.length >= 2) {
        generate_page_tab_bool = true;
    } else {
        generate_page_tab_bool = false;
    }

    // Only proceed to manipulate page if page tabs should be generated.
    if (generate_page_tab_bool) {
        // Create parent tab container.
        var page_tabs = document.createElement("nav");
        page_tabs.className = "pagetabs-tab-container";
        page_tabs_ul = document.createElement("ul")
        page_tabs.appendChild(page_tabs_ul);

        // Create parent content container.
        var page_divs = document.createElement("div");
        page_divs.className = "pagetabs-content-container";

        // Default "All" tab. Will always be present in a page tabs page.
        // Create tab for "All".
        var all_tab = document.createElement("li");
        all_tab.id = "pagetabs-" + element_num + "-all-tab";
        all_tab.className = "pagetabs-tab-element";
        all_tab.innerHTML = "All";
        page_tabs_ul.append(all_tab);

        // Create page content div for "All".
        var all_div = document.createElement("div");
        all_div.id = "pagetabs-" + element_num + "-all-div";
        all_div.className = "pagetabs-content-element";
        var all_arr_length = pagetabs_header_dict["All"].length;
        for (index = 0; index < all_arr_length; index++) {
            all_div.appendChild(pagetabs_header_dict["All"][index]);
        }
        page_divs.append(all_div);

        // In most cases, we will have an automatically generated "Other" tab, too.
        // Create tab for "Other".
        var other_tab = document.createElement("li");
        other_tab.id = "pagetabs-" + element_num + "-other-tab";
        other_tab.className = "pagetabs-tab-element";
        other_tab.innerHTML = "Other";

        // Create page content for "Other".
        var other_div = document.createElement("div");
        other_div.id = "pagetabs" + element_num + "-other-div";
        other_div.className = "pagetabs-content-element";

        // Loop through all values present in ordering array to dynamically add all other headers.
        // Looping through this way ensures we preserve page content ordering.
        for (var index = 0; index < pagetabs_header_ordering.length; index++) {

            // Check if header item is in "tabbable topics" array.
            if (allow_all_headers || page_tabbable_topics.includes(pagetabs_header_ordering[index])) {
                // Item is in "tabbable topics" array. We can create a new page tab for this content.
                var curr_header = pagetabs_header_ordering[index];
                var header_slug = slugify_text(curr_header);

                // Create tab for current header.
                var curr_tab = document.createElement("li");
                curr_tab.id = "pagetabs-" + element_num + "-" + header_slug + "-tab";
                curr_tab.className = "pagetabs-tab-element";
                curr_tab.innerHTML = curr_header;
                page_tabs_ul.append(curr_tab);

                // Create page content div for current header.
                var curr_div = document.createElement("div");
                curr_div.id = "pagetabs-" + element_num + "-" + header_slug + "-div";
                curr_div.className = "pagetabs-content-element";
                var array_length = pagetabs_header_dict[curr_header].length;
                for (var inner_index = 0; inner_index < array_length; inner_index++) {
                    curr_div.appendChild(pagetabs_header_dict[curr_header][inner_index]);
                }
                page_divs.append(curr_div);

            } else {
                // Item is not in "tabbable topics" array. Put content into "Other" tab.
                var array_length = pagetabs_header_dict["Other"].length;
                for (var inner_index = 0; inner_index < array_length; inner_index++) {
                    other_div.appendChild(pagetabs_header_dict["Other"][inner_index]);
                }
            }
        }

        // Check if "other" section was populated at all. If so, append to main pagetab containers.
        if (other_div.childElementCount > 0) {
            // Other tab has elements and should exist.
            page_tabs_ul.append(other_tab);
            page_divs.append(other_div);
        } else if (pagetabs_header_ordering.includes("Other")) {
            // "Other" tab does not have elements and should not exist.
            pagetabs_header_ordering.splice("Other", 1);
        }

        // Make sure nothing is in container element so we can rebuild it. Everything should be processed by now.
        while (pagetab_content_container.firstChild) {
            pagetab_content_container.removeChild(pagetab_content_container.firstChild);
        }

        // Finally, append elements to page itself.
        pagetab_content_container.appendChild(page_tabs);
        pagetab_content_container.appendChild(page_divs);

        // Add "All" value to start of array.
        // If we have tabs at all, then this is always present and first.
        pagetabs_header_ordering.unshift("All");
        current_tab_parent = document.getElementsByClassName("pagetabs-tab-container")[element_num].childNodes[0];

        // Add click event listeners for pagetabs.
        for (var index = 0; index < pagetabs_header_ordering.length; index++) {
            // Get tab elements.
            var current_tab = current_tab_parent.childNodes[index];

            // Add click handling to tab elements.
            current_tab.addEventListener("click", function() {
                // Get index of clicked tab element.
                // Do this by cycling back through parent container until we get to first child, and counting each.

                var element_index = 0;
                var current_tab = this;
                while (current_tab.previousSibling != null) {
                    current_tab = current_tab.previousSibling;
                    element_index++;
                }

                // Hide all div tab-sections, except the one clicked.
                for (var tab_index = 0; tab_index < pagetabs_header_ordering.length; tab_index++) {
                    // Get parent of content elements to hide/show.
                    content_container = document.getElementsByClassName("pagetabs-content-container")[element_num];

                    // Check if same index as clicked. If so, show instead.
                    if (element_index == tab_index) {
                        // On clicked element. Set to "block" to display.
                        content_container.childNodes[tab_index].style.display = "block";
                    } else {
                        // On a sibling element. Set to display none to hide.
                        content_container.childNodes[tab_index].style.display = "none";
                    }
                }
            });

            // Also hide all content, initially. Otherwise we'll have duplicates on page.
            var tab_content = document.getElementsByClassName("pagetabs-content-container")[element_num].childNodes[index];
            tab_content.style.display = "none";
        }

        // Set "All" content to be visible. Everything else should be hidden by now.
        document.getElementsByClassName("pagetabs-content-container")[element_num].childNodes[0].style.display = "block";
    }
}


/**
 * Takes given text string and returns equivalent "slug" version.
 *
 * Slugs are safe for urls and html id's.
 * Essentially, all letters are converted to lowercase, and whitespace is converted to dashes.
 */
function slugify_text(orig_text) {
    return orig_text.toLowerCase().replace(/ /g, "-");
}


// Run "page Tab Generation" logic.
page_tab_generation_main();
