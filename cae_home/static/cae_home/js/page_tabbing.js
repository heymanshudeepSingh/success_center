
/**
 * JavaScript Logic for custom "page tabbing" CSS elements.
 *
 * By default, it will create tabs for all H2 element direct children.
 */


// Global Variables.
window.cae_vars['pageTabbing__headerDict'] = {      // Dict to hold all parsed tab header values.
    "All": [],
    "Other": [],
};
window.cae_vars['pageTabbing__allowAllHeaders'] = true;     // Bool indicating if h2 headers get lumped into "other".
window.cae_vars['pageTabbing__headerOrdering'] = [];        // Array to preserve ordering of tab headers.
window.cae_vars['pageTabbing__topics'] =[];                 // List of "allowed" topics if lumping into "other".
window.cae_vars['pageTabbing__generatationBool'] = true;    // Bool saving if we should generate tabs to begin with.


/**
 * The start of page tabbing logic.
 */
window.cae_functions['pageTabbing__pageTabGenerationMain'] = function () {
    // Get default pagetab content container.
    let pagetab_content_containers = document.getElementsByClassName("page-tabs");
    let index = 0;

    // Handle for each pagetab container found on page. This allows multiple to exist on a page, if desired.
    for (index = 0; index < pagetab_content_containers.length; index++) {
        // Populate variables.
        window.cae_vars['pageTabbing__headerDict'] = {
            "All": [],
            "Other": [],
        };
        window.cae_vars['pageTabbing__headerOrdering'] = [];
        window.cae_vars['pageTabbing__topics'] = [];

        // Get tabbable topics, if provided.
        let tabbable_topics = pagetab_content_containers[index].dataset.headers;
        if (tabbable_topics != null && tabbable_topics != "") {
            // Header topics provided. Parse and use that for tabbing.
            window.cae_vars['pageTabbing__allowAllHeaders'] = false;
            window.cae_vars['pageTabbing__topics'] = tabbable_topics.split(", ");
        } else {
            // Header topics not provided. Default to using all found H2 elements.
            window.cae_vars['pageTabbing__allowAllHeaders'] = true;
        }

        window.cae_functions['pageTabbing__populatePageTabVariables'](pagetab_content_containers[index]);
        window.cae_functions['pageTabbing__generatePageTabs'](pagetab_content_containers[index], index);
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
window.cae_functions['pageTabbing__populatePageTabVariables'] = function(pagetab_content_container) {
    let current_header = "Other";
    let index = 0;

    // Loop through all child content elements.
    let page_length = pagetab_content_container.childNodes.length;
    for (index = 0; index < page_length; index++) {
        // Save current element for easy reference.
        let current_element = pagetab_content_container.childNodes[index];

        // Check if element is empty. We can skip these.
        if (current_element.nodeName == "#text" && current_element.data.trim() == "") {
            // Pass. Is empty element. We probably don't want to include this.

        // Proceed if element has content.
        } else {
            // Check if element is H2 header. If so, create a new key in header_dict, using element's text value.
            if (current_element.tagName == "H2") {
                current_header = current_element.firstChild.nodeValue;

                // Check if item is in "tabbable topics" array. By default, all headers are allowed.
                if (
                    window.cae_vars['pageTabbing__allowAllHeaders'] ||
                    window.cae_vars['pageTabbing__topics'].includes(current_header)
                ) {
                    // Item is in "tabbable topics" array. We can create a new page tab for this content.
                    // Create new key with header value, and also push to ordering dict to preserve page content ordering.
                    window.cae_vars['pageTabbing__headerDict'][current_header] = [];
                    window.cae_vars['pageTabbing__headerOrdering'].push(current_header);
                } else {
                    // Item is not in "tabbable topics" array. Put content into "Other" tab.
                    current_header = "Other";
                }
            }

            // Add element into "all" key.
            window.cae_vars['pageTabbing__headerDict']["All"].push(pagetab_content_container.childNodes[index].cloneNode(true));
            // Also add element to dictionary, under current found header.
            window.cae_vars['pageTabbing__headerDict'][current_header].push(pagetab_content_container.childNodes[index]);
        }
    }

    // Check if any elements were added to "Other" section. If so, add "Other" to list of dict values.
    if (window.cae_vars['pageTabbing__headerDict']["Other"].length > 0) {
        window.cae_vars['pageTabbing__headerOrdering'].push("Other");
    }
}


/**
 * Generates actual tab navigation elements on page.
 */
window.cae_functions['pageTabbing__generatePageTabs'] = function(pagetab_content_container, element_num) {
    let index = 0;
    let inner_index = 0;
    let tab_index = 0;

    // Check if we have at least two unique headers to create tabs for.
    // If so, generate pagetabs html. Otherwise, leave page as is.
    let header_array_clone = window.cae_vars['pageTabbing__headerOrdering'].slice();

    // We don't want to count the "Other" tab for counting purposes. It may or may not be present.
    if (header_array_clone.includes("Other")) {
        index = header_array_clone.indexOf("Other");
        header_array_clone.splice(index, 1);
    }

    // Now that we have an array of only "unique" tab values, check length.
    if (header_array_clone.length >= 2) {
        window.cae_vars['pageTabbing__generatationBool'] = true;
    } else {
        window.cae_vars['pageTabbing__generatationBool'] = false;
    }

    // Only proceed to manipulate page if page tabs should be generated.
    if (window.cae_vars['pageTabbing__generatationBool']) {
        // Create parent tab container.
        let page_tabs = document.createElement("nav");
        page_tabs.className = "pagetabs-tab-container";
        page_tabs_ul = document.createElement("ul")
        page_tabs.appendChild(page_tabs_ul);

        // Create parent content container.
        let page_divs = document.createElement("div");
        page_divs.className = "pagetabs-content-container";

        // Default "All" tab. Will always be present in a page tabs page.
        // Create tab for "All".
        let all_tab = document.createElement("li");
        all_tab.id = "pagetabs-" + element_num + "-all-tab";
        all_tab.className = "pagetabs-tab-element selected";
        all_tab.innerHTML = "All";
        page_tabs_ul.append(all_tab);

        // Create page content div for "All".
        let all_div = document.createElement("div");
        all_div.id = "pagetabs-" + element_num + "-all-div";
        all_div.className = "pagetabs-content-element";
        let all_arr_length = window.cae_vars['pageTabbing__headerDict']["All"].length;
        for (index = 0; index < all_arr_length; index++) {
            all_div.appendChild(window.cae_vars['pageTabbing__headerDict']["All"][index]);
        }
        page_divs.append(all_div);

        // In most cases, we will have an automatically generated "Other" tab, too.
        // Create tab for "Other".
        let other_tab = document.createElement("li");
        other_tab.id = "pagetabs-" + element_num + "-other-tab";
        other_tab.className = "pagetabs-tab-element";
        other_tab.innerHTML = "Other";

        // Create page content for "Other".
        let other_div = document.createElement("div");
        other_div.id = "pagetabs" + element_num + "-other-div";
        other_div.className = "pagetabs-content-element";

        // Loop through all values present in ordering array to dynamically add all other headers.
        // Looping through this way ensures we preserve page content ordering.
        for (index = 0; index < window.cae_vars['pageTabbing__headerOrdering'].length; index++) {

            // Check if header item is in "tabbable topics" array.
            if (
                window.cae_vars['pageTabbing__allowAllHeaders'] ||
                window.cae_vars['pageTabbing__topics'].includes(window.cae_vars['pageTabbing__headerOrdering'][index])
            ) {
                // Item is in "tabbable topics" array. We can create a new page tab for this content.
                let curr_header = window.cae_vars['pageTabbing__headerOrdering'][index];
                let header_slug = window.cae_functions['pageTabbing__slugifyText'](curr_header);

                // Create tab for current header.
                let curr_tab = document.createElement("li");
                curr_tab.id = "pagetabs-" + element_num + "-" + header_slug + "-tab";
                curr_tab.className = "pagetabs-tab-element";
                curr_tab.innerHTML = curr_header;
                page_tabs_ul.append(curr_tab);

                // Create page content div for current header.
                let curr_div = document.createElement("div");
                curr_div.id = "pagetabs-" + element_num + "-" + header_slug + "-div";
                curr_div.className = "pagetabs-content-element";
                let array_length = window.cae_vars['pageTabbing__headerDict'][curr_header].length;
                for (inner_index = 0; inner_index < array_length; inner_index++) {
                    curr_div.appendChild(window.cae_vars['pageTabbing__headerDict'][curr_header][inner_index]);
                }
                page_divs.append(curr_div);

            } else {
                // Item is not in "tabbable topics" array. Put content into "Other" tab.
                let array_length = window.cae_vars['pageTabbing__headerDict']["Other"].length;
                for (inner_index = 0; inner_index < array_length; inner_index++) {
                    other_div.appendChild(window.cae_vars['pageTabbing__headerDict']["Other"][inner_index]);
                }
            }
        }

        // Check if "other" section was populated at all. If so, append to main pagetab containers.
        if (other_div.childElementCount > 0) {
            // Other tab has elements and should exist.
            page_tabs_ul.append(other_tab);
            page_divs.append(other_div);
        } else if (window.cae_vars['pageTabbing__headerOrdering'].includes("Other")) {
            // "Other" tab does not have elements and should not exist.
            window.cae_vars['pageTabbing__headerOrdering'].splice("Other", 1);
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
        window.cae_vars['pageTabbing__headerOrdering'].unshift("All");
        current_tab_parent = document.getElementsByClassName("pagetabs-tab-container")[element_num].childNodes[0];

        // Add click event listeners for pagetabs.
        for (index = 0; index < window.cae_vars['pageTabbing__headerOrdering'].length; index++) {
            // Get tab elements.
            let current_tab = current_tab_parent.childNodes[index];

            // Add click handling to tab elements.
            current_tab.addEventListener("click", function() {
                // Get index of clicked tab element.
                // Do this by cycling back through parent container until we get to first child, and counting each.

                let element_index = 0;
                let current_tab = this;
                while (current_tab.previousSibling != null) {
                    current_tab = current_tab.previousSibling;
                    element_index++;
                }

                // Hide all div tab-sections, except the one clicked.
                for (tab_index = 0; tab_index < window.cae_vars['pageTabbing__headerOrdering'].length; tab_index++) {
                    // Get parent of content elements to hide/show.
                    let tab_container = this.parentNode;
                    let content_container = document.getElementsByClassName("pagetabs-content-container")[element_num];

                    // Check if same index as clicked. If so, show instead.
                    if (element_index == tab_index) {
                        // On clicked element.

                        // Add selected class to tab.
                        $(tab_container.childNodes[tab_index]).addClass("selected");

                        // Set to content to display.
                        $(content_container.childNodes[tab_index]).slideDown();
                    } else {
                        // On a sibling element.

                        // Remove selected class, if present.
                        $(tab_container.childNodes[tab_index]).removeClass("selected");

                        // Set content to hide.
                        $(content_container.childNodes[tab_index]).slideUp();

                    }
                }
            });

            // Also hide all content, initially. Otherwise we'll have duplicates on page.
            let tab_content = document.getElementsByClassName("pagetabs-content-container")[element_num].childNodes[index];
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
window.cae_functions['pageTabbing__slugifyText'] = function(orig_text) {
    return orig_text.toLowerCase().replace(/ /g, "-");
}


// Run "page Tab Generation" logic.
window.cae_functions['pageTabbing__pageTabGenerationMain']();
