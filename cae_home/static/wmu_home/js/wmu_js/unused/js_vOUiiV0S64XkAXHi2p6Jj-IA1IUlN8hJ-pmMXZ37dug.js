(function($) {

  // Behavior to load FlexSlider
  Drupal.behaviors.flexslider = {
    attach: function(context, settings) {
      var sliders = [];
      if ($.type(settings.flexslider) !== 'undefined' && $.type(settings.flexslider.instances) !== 'undefined') {

        for (id in settings.flexslider.instances) {

          if (settings.flexslider.optionsets[settings.flexslider.instances[id]] !== undefined) {
            if (settings.flexslider.optionsets[settings.flexslider.instances[id]].asNavFor !== '') {
              // We have to initialize all the sliders which are "asNavFor" first.
              _flexslider_init(id, settings.flexslider.optionsets[settings.flexslider.instances[id]], context);
            } else {
              // Everyone else is second
              sliders[id] = settings.flexslider.optionsets[settings.flexslider.instances[id]];
            }
          }
        }
      }
      // Slider set
      for (id in sliders) {
        _flexslider_init(id, settings.flexslider.optionsets[settings.flexslider.instances[id]], context);
      }
    }
  };

  /**
   * Initialize the flexslider instance
   */

  function _flexslider_init(id, optionset, context) {
    $('#' + id, context).once('flexslider', function() {
      // Remove width/height attributes
      // @todo load the css path from the settings
      $(this).find('ul.slides > li > *').removeAttr('width').removeAttr('height');

      if (optionset) {
        // Add events that developers can use to interact.
        $(this).flexslider($.extend(optionset, {
          start: function(slider) {
            slider.trigger('start');
          },
          before: function(slider) {
            slider.trigger('before');
          },
          after: function(slider) {
            slider.trigger('after');
          },
          end: function(slider) {
            slider.trigger('end');
          },
          added: function(slider) {
            slider.trigger('added');
          },
          removed: function(slider) {
            slider.trigger('removed');
          }
        }));
      } else {
        $(this).flexslider();
      }
    });
  }

}(jQuery));
;
/**
 * @file
 * AddThis javascript actions.
 */

(function ($) {
  Drupal.behaviors.addthis = {
    scriptLoaded: false,

    attach: function(context, settings) {

      // The addthis configuration is not loaded but the settings are passed
      // to do so.
      if (!this.isConfigLoaded() && this.isSettingsLoaded()) {
        // Initialize config.
        this.initConfig();

        // Load widget js.
        if (!this.scriptLoaded) {
          this.loadDomready();
        }
      }
      // The addthis configuration is not loaded but no setting are available
      // to load anything.
      else if(!this.isConfigLoaded() && !this.isSettingsLoaded()) {
        // Do nothing
      }

      // Trigger ready on ajax attach.
      if (context != window.document) {
        Drupal.behaviors.addthis.ajaxLoad(context, settings);
      }

    },

    // Returns if the settings defined by the addthis module are loaded.
    isSettingsLoaded: function () {
      if (typeof Drupal.settings.addthis == 'undefined') {
        return false;
      }
      return true;
    },

    // Returns if the configuration variables needed for widget.js are defined.
    isConfigLoaded: function() {
      if (typeof addthis_config == 'undefined' || typeof addthis_share == 'undefined') {
        return false;
      }
      return true;
    },

    initConfig: function () {
      addthis_config = Drupal.settings.addthis.addthis_config;
      addthis_share = Drupal.settings.addthis.addthis_share;
    },

    // Load the js library when the dom is ready.
    loadDomready: function() {
      // If settings asks for loading the script after the dom is loaded, then
      // load the script here.
      if (!this.scriptLoaded &&
          this.isConfigLoaded() &&
          Drupal.settings.addthis.domready) {
        $.getScript(Drupal.settings.addthis.widget_url, Drupal.behaviors.addthis.scriptReady);
      }
    },

    // Callback for loading the widget.js dynamically.
    scriptReady: function () {
      this.scriptLoaded = true;

      if (!typeof(addthis) != 'undefined') {
        // Give the chance to other scripts to hook into the addthis variable.
        $(document).trigger('addthis.init', addthis);
      }
    },

    // Called when a ajax request returned.
    ajaxLoad: function(context, settings) {
      if (typeof window.addthis != 'undefined' &&
          typeof window.addthis.toolbox == 'function')
      {
          window.addthis.toolbox('.addthis_toolbox');
      }
    }

  };

  // This load the config in time to run any addthis functionality.
  if (Drupal.behaviors.addthis.isConfigLoaded()) {
    addthis_config = Drupal.settings.addthis.addthis_config;
    addthis_share = Drupal.settings.addthis.addthis_share;
  }

  // Document ready in case we want to load AddThis into the dom after every
  // thing is loaded.
  //
  // Is executed once after the attach happened.
  $(document).ready(function() {
    Drupal.behaviors.addthis.loadDomready();
  });

}(jQuery));
;
