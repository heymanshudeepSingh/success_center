/**
 * JavaScript to allow collapsing of Django field list filters.
 * Defaults to having filter items collapsed.
 *
 * Source from:
 *  https://stackoverflow.com/questions/6086651/minimize-the-list-filter-in-django-admin
 *  https://gist.github.com/jjdelc/985283
 *  https://github.com/peppelinux/Django-snippets/blob/master/django-admin.js-snippets/menu_filter_collapse.js
 */


/**
 * Basic example of getting Django JQuery to load before logic.
 *
 * window.on('load') - Necessary or else Django template might try to load JS before JQuery.
 * (function($) {...})(django.jQuery); - Necessary or else JQuery might not be fully initialized yet and give errors.
 */
//;$(window).on('load', function() {
//    (function($) {
//        $('#changelist-filter').children('h3').each(function(){
//            var $title = $(this);
//            $title.click(function(){
//                $title.next().slideToggle();
//            });
//        });
//    })(django.jQuery);
//});


/**
 * Logic to create collapsable list filter class.
 */
$(window).on('load', function() {
    (function($){

        var list_filter_element = '#changelist-filter';
        var list_filter_header = 'h2'
        var list_filter_section_title = 'h3'

        // Needed for full table resize after filter menu collapse.
        var change_list = '#changelist'


        ListFilterCollapsePrototype = {
            bindToggle: function(){
                var that = this;
                this.$filterTitle.click(function(){

                    if ( ! $(list_filter_element).is(':hidden') ) {
                        $(this).css('position', 'relative');
                    } else {
                        $(this).css('position', 'absolute');
                    }

                    // Check if some ul is collapsed.
                    // Open it before slidetoggle all together.
                    $(list_filter_element).children('ul').each(function(){
                        if ($(this).is(':hidden')) {
                            $(this).slideToggle('fast', 'linear');
                        }
                    })

                    // Now slidetoggle all.
                    that.$filterContentTitle.slideToggle();
                    that.$filterContentElements.slideToggle('fast', 'swing');
                    that.$list.toggleClass('filtered');
                });

            },
            init: function(filterEl) {
                this.$filterTitle = $(filterEl).children(list_filter_header);
                this.$filterContentTitle = $(filterEl).children(list_filter_section_title);
                this.$filterContentElements = $(filterEl).children('ul');
                $(this.$filterTitle).css('cursor', 'pointer');
                this.$list = $(change_list);

                // Header collapse.
                this.bindToggle();

                // Create collapsable children.
                $(list_filter_element).children(list_filter_section_title).each(function() {
                    var $title = $(this);
                    var child_toggled = false;
                    $title.click(function() {
                        $title.next().slideToggle('fast', 'swing');
                    });

                    $title.css('border-bottom', '1px solid grey');
                    $title.css('padding-bottom', '5px');
                    $title.css('cursor', 'pointer');
                });

            }
        }


        function ListFilterCollapse(filterEl) {
            this.init(filterEl);
        }
        ListFilterCollapse.prototype = ListFilterCollapsePrototype;


        $(document).ready(function(){
            $(list_filter_element).each(function() {
                var collapser = new ListFilterCollapse(this);
                $(this).css('position', 'absolute');
                $(this).css('right', '25px');
            });

            // Close them by default.
            $(list_filter_element + ' ' + list_filter_header).click();

            // If some filter was clicked it will be visible for first run only.
            $(list_filter_element).children(list_filter_section_title).each(function(){

                lis = $(this).next().children('li')
                lis.each(function(count) {
                    if (count > 0) {
                        if ($(this).hasClass('selected')) {
                            $(this).parent().slideDown('fast', 'swing');
                            $(this).parent().prev().slideDown('fast', 'swing');

                            // If some filters are active, every section title (h3) should be visible.
                            $(list_filter_element).children(list_filter_section_title).each(function() {
                                $(this).slideDown('fast', 'swing');
                            })

                            $(change_list).toggleClass('filtered');
                        }
                    }
                })

            });

        });
    })(django.jQuery);
});
