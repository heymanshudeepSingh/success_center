# Django - CAE Workspace > CAE Home > Static

## Description
Location for "Static" content, such as css, images, and more.

Essentially, these are files that the end user gets as-is from a url, as opposed to, say, a template which is first
processed by the framework before being rendered.

Static content is almost always grabbed by the template at page load.


## Extending Base Static File Blocks

### CSS and Font Files
To include special css or font files on a given page, simply override the ``extra_styles`` or ``extra_fonts`` blocks in the
html templates.

These blocks are empty by default and provided specifically for this functionality.

### JS Files
Due to the nature of JS, there are two block locations to potentially override:

* ``extra_scripts`` - Located in head metadata. Will be run before content loads. Place JS files here if they do not
expect specific body elements to exist, and can generally be run before the page loads.
* ``extra_scripts_body`` - Located after the body element. Will be run after a majority of page content loads. Place JS
files here if they rely on specific body elements existing, or if they rely on other JS files.

These blocks are empty by default and provided specifically for this functionality.


## Special Content Element Types

### Status Messages
For displaying messages to user at top of page. Generally used automatically through Django's built-in messages
framework.

If created in template, then will be automatically targeted by respective JS code. Can be manually called by including
the ``cae_home/include/status_messages`` template.

Adding status messages to page after page load is not currently supported.

### Overlay Modals
For greying out the screen and then displaying important information to user.

Populate one of two ways:
* In templating, by overriding the ``overlay_modal`` block.
* After page load, by appending elements to the ``#overlay_modal`` element.

Can use JS functions ``show_overlay_modal()`` and ``hide_overlay_modal()`` to show/hide the overlay. For example,
you implement logic to call these functions on button click, etc.

### Side Content Bars
For displaying supplementary information to the user. Elements can be added to side bars by overriding the
``content_bar_left`` and ``content_bar_right`` blocks. If content bars are empty on page load, they are automatically
removed from DOM via JS.

Content bars auto-hide by default. If hidden, a clickable arrow will appear on the left or right side of the screen
(depending on which side's content bar is present). Clicking this arrow will show the respective content bar.
