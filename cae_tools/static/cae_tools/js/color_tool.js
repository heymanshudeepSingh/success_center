(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
/**
 * Functions to convert color definitions.
 *
 * Warning: Conversions to/from HSL use rounding, and thus may lose precision.
 *      As result, converting to HSL and back may not return exact original value,
 *      but should be fairly close.
 */

var hex_value;
var rgb_value;
var hsl_value;

var color_parse = exports.color_parse = {

    /**
     * Parses a hex string for validity..
     * :return: A valid hex string, or Null if value was invalid.
     */
    parse_hex_string: function parse_hex_string(hex_value) {

        // Check start of string.
        if (hex_value[0] == '#') {
            hex_value = hex_value.substring(1, 7);
        }

        if (hex_value.length != 6) {
            hex_value = null;
        }

        if (hex_value != null) {
            // Check each character for validity.
            for (var index = 0; index < hex_value.length; index++) {
                if (hex_value != null) {
                    var char_value = hex_value.charCodeAt(index);
                    var valid_char = false;

                    if (char_value >= 48 && char_value <= 57) {
                        valid_char = true;
                    } else if (char_value >= 65 || char_value <= 70) {
                        valid_char = true;
                    } else if (char_value >= 97 || char_value <= 102) {
                        valid_char = true;
                    }

                    if (valid_char == false) {
                        hex_value = null;
                    }
                }
            }

            return '#' + hex_value;
        }

        return null;
    },

    /**
     * Parses a rgb string and returns an array of [red, green, blue] values.
     * :return: An array of rgb values, or Null if values were invalid.
     */
    parse_rgb_string: function parse_rgb_string(rgb_value) {

        // Check if value is string or already parsed as array.
        if (Array.isArray(rgb_value)) {
            // Found array.
            var rgb_array = rgb_value;
        } else {
            // Found string. Split to array.
            if (rgb_value[0] == '(') {
                // Encased in parenthesis.
                var rgb_array = rgb_value.substring(4, rgb_value.length - 1).split(', ').map(Number);

                // Try again if no spaces were present.
                if (rgb_array.length == 1) {
                    rgb_array = rgb_value.substring(4, rgb_value.length - 1).split(',').map(Number);
                }
            } else {
                // Not encased in parenthesis.
                var rgb_array = rgb_value.split(', ').map(Number);

                // Try again if no spaces were present.
                if (rgb_array.length == 1) {
                    rgb_array = rgb_value.split(',').map(Number);
                }
            }
        }

        // Check that array has exactly 3 values.
        if (rgb_array.length == 3) {

            // Ensure individual values are integers and in valid ranges.
            if (!Number.isInteger(rgb_array[0]) || rgb_array[0] < 0 || rgb_array[0] > 255 || !Number.isInteger(rgb_array[0]) || rgb_array[1] < 0 || rgb_array[1] > 255 || !Number.isInteger(rgb_array[0]) || rgb_array[2] < 0 || rgb_array[2] > 255) {
                // One or more values were invalid.
                console.warn('Unable to parse rgb values: ' + rgb_array);
                rgb_array = null;
            }
        } else {
            rgb_array = null;
            console.warn('Unable to parse rgb values: ' + rgb_array);
        }

        return rgb_array;
    },

    /**
     * Parses a hsl string and returns an array of [hue, sat, light] values.
     * :return: An array of hsl values, or Null if values were invalid.
     */
    parse_hsl_string: function parse_hsl_string(hsl_value) {

        // Check if value is string or already parsed as array.
        if (Array.isArray(hsl_value)) {
            // Found array.
            var hsl_array = hsl_value;
        } else {
            if (hsl_value[0] == '(') {
                // Found string. Split to array.
                var hsl_array = hsl_value.substring(4, hsl_value.length - 1).split(', ').map(Number);

                // Try again if no spaces were present.
                if (hsl_array.length == 1) {
                    hsl_array = hsl_value.substring(4, hsl_value.length - 1).split(',').map(Number);
                }
            } else {
                // Found string. Split to array.
                var hsl_array = hsl_value.split(', ').map(Number);

                // Try again if no spaces were present.
                if (hsl_array.length == 1) {
                    hsl_array = hsl_value.split(',').map(Number);
                }
            }
        }

        // Check that array has exactly 3 values.
        if (hsl_array.length == 3) {

            // Ensure individual values are integers and in valid ranges.
            if (!Number.isInteger(hsl_array[0]) || hsl_array[0] < 0 || hsl_array[0] > 360 || !Number.isInteger(hsl_array[0]) || hsl_array[1] < 0 || hsl_array[1] > 100 || !Number.isInteger(hsl_array[0]) || hsl_array[2] < 0 || hsl_array[2] > 100) {
                // One or more values were invalid.
                console.warn('Unable to parse hsl values: ' + hsl_array);
                hsl_array = null;
            }
        } else {
            hsl_array = null;
            console.warn('Unable to parse hsl values: ' + hsl_array);
        }

        return hsl_array;
    },

    /**
     * Validates for HSL array.
     * :return: True on valid or False on invalid.
     */
    validate_for_HSL: function validate_for_HSL(value) {

        // Check that value is array.
        if (Array.isArray(value)) {
            // Check that array is exactly 3 elements long.
            if (value.length != 3) {
                console.warn('Invalid HSL array passed: ' + value);
                return false;
            }
        } else {
            console.warn('Expected array of HSL format. Instead got: ' + value);
            return false;
        }

        return true;
    }
};

var color_calc = exports.color_calc = {

    /**
     * Converts values from hex (#xxyyzz) to rgb (x, y, z).
     */
    convert_hex_to_rgb: function convert_hex_to_rgb(hex_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        // Convert values.
        var red = parseInt(hex_value.slice(1, 3), 16);
        var green = parseInt(hex_value.slice(3, 5), 16);
        var blue = parseInt(hex_value.slice(5, 7), 16);
        // var rgb_value = 'rgb(' + red + ', ' + green + ', ' + blue + ')';
        var rgb_value = [red, green, blue];

        // Print and return results.
        if (print_result) {
            console.log('[hex_to_rgb] Converted ' + hex_value + ' to ' + rgb_value + '.');
        }
        return rgb_value;
    },

    /**
     * Converts values from rgb (x, y, z) to hex (#xxyyzz).
     */
    convert_rgb_to_hex: function convert_rgb_to_hex(rgb_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        // Parse values.
        var rgb_array = color_parse.parse_rgb_string(rgb_value);

        // Check that values were parsed properly.
        if (rgb_array != null) {
            // Convert values.
            var red = rgb_array[0].toString(16);
            var green = rgb_array[1].toString(16);
            var blue = rgb_array[2].toString(16);

            // Pad with 0 if hex value is only one character long.
            if (red.length == 1) {
                red = '0' + red;
            }
            if (green.length == 1) {
                green = '0' + green;
            }
            if (blue.length == 1) {
                blue = '0' + blue;
            }

            // Concatenate into hex.
            hex_value = '#' + red + green + blue;

            // Print and return results.
            if (print_result) {
                console.log('[rgb_to_hex] Converted ' + rgb_value + ' to ' + hex_value + '.');
            }
            return hex_value;
        } else {
            return null;
        }
    },

    /**
     * Converts values from rgb (x, y, z) to hsl (x, y, z).
     */
    convert_rgb_to_hsl: function convert_rgb_to_hsl(rgb_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        // Parse values.
        var rgb_array = color_parse.parse_rgb_string(rgb_value);
        var red = rgb_array[0] / 255;
        var green = rgb_array[1] / 255;
        var blue = rgb_array[2] / 255;

        // Convert values.
        var min = Math.min(red, green, blue);
        var max = Math.max(red, green, blue);
        var lightness = (min + max) / 2;
        var difference = 0;

        if (min == max) {
            // Achromatic. Hue and sat are 0.
            var hue = 0;
            var saturation = 0;
        } else {
            // Chromatic. Need to calculate all values.
            // Calculate saturation values.
            difference = max - min;
            if (lightness > 0.5) {
                var saturation = difference / (2 - max - min);
            } else {
                var saturation = difference / (max + min);
            }

            // Calculate hue based on differences between red/green/blue.
            switch (max) {
                case red:
                    var hue = (green - blue) / difference + (green < blue ? 6 : 0);
                    break;
                case green:
                    var hue = (blue - red) / difference + 2;
                    break;
                case blue:
                    var hue = (red - green) / difference + 4;
                    break;
            }
            hue /= 6;
        }

        // Adjust values from between 0 and 1 to:
        // Between 0 and 360 for hue, between 0 and 100 for saturation/lightness.
        hue = Math.round(hue * 360);
        saturation = Math.round(saturation * 100);
        lightness = Math.round(lightness * 100);
        hsl_value = [hue, saturation, lightness];

        // Print and return results.
        if (print_result) {
            console.log('[rgb_to_hsl] Converted ' + rgb_value + ' to ' + hsl_value + '.');
        }
        return hsl_value;
    },

    /**
     * Converts values from rgb (x, y, z) to hsl (x, y, z).
     */
    convert_hsl_to_rgb: function convert_hsl_to_rgb(hsl_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        // Parse values.
        var hsl_array = color_parse.parse_hsl_string(hsl_value);
        var hue = hsl_array[0];
        var saturation = hsl_array[1];
        var lightness = hsl_array[2];

        // Convert values back to between 0 and 1, if not already.
        if (hue > 1) {
            hue /= 360;
        }
        if (saturation > 1) {
            saturation /= 100;
        }
        if (lightness > 1) {
            lightness /= 100;
        }

        if (saturation == 0) {
            // Achromatic.
            var red = lightness;
            var green = lightness;
            var blue = lightness;
        } else {
            // Chromatic.
            // I don't know what this does. It's basically magic, but seems to work.
            var hue2rgb = function hue2rgb(p, q, t) {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1 / 6) return p + (q - p) * 6 * t;
                if (t < 1 / 2) return q;
                if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
                return p;
            };

            var q = lightness < 0.5 ? lightness * (1 + saturation) : lightness + saturation - lightness * saturation;
            var p = 2 * lightness - q;

            var red = hue2rgb(p, q, hue + 1 / 3);
            var green = hue2rgb(p, q, hue);
            var blue = hue2rgb(p, q, hue - 1 / 3);
        }

        red = Math.round(red * 255);
        green = Math.round(green * 255);
        blue = Math.round(blue * 255);
        rgb_value = [red, green, blue];

        // Print and return results.
        if (print_result) {
            console.log('[hsl_to_rgb] Converted ' + hsl_value + ' to ' + rgb_value + '.');
        }
        return rgb_value;
    },

    /**
     * Converts values from hex (#xxyyzz) to hsl (x, y, z).
     */
    convert_hex_to_hsl: function convert_hex_to_hsl(hex_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        var rgb_value = convert_hex_to_rgb(hex_value);
        var hsl_value = convert_rgb_to_hsl(rgb_value);

        // Print and return results.
        if (print_result) {
            console.log('[hex_to_hsl] Converted ' + hex_value + ' to ' + hsl_value + '.');
        }
        return hsl_value;
    },

    /**
     * Converts values from hsl (x, y, z) to hex (#xxyyzz).
     */
    convert_hsl_to_hex: function convert_hsl_to_hex(hsl_value) {
        var print_result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;


        var rgb_value = convert_hsl_to_rgb(hsl_value);
        var hex_value = convert_rgb_to_hex(rgb_value);

        // Print and return results.
        if (print_result) {
            console.log('[hsl_to_hex] Converted ' + hsl_value + ' to ' + hex_value + '.');
        }
        return hex_value;
    },

    /**
     * Convert arg 1 to match hue of arg 2.
     */
    adjust_color_hue: function adjust_color_hue(old_color, desired_hue) {
        var print_result = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

        var valid_input = false;
        var new_color = null;

        // Validate old color as HSL array.
        if (color_parse.validate_for_HSL(old_color)) {

            // Check if desired is in HSL format.
            if (Array.isArray(desired_hue)) {
                if (color_parse.validate_for_HSL(desired_hue)) {
                    // Valid HSL array.
                    valid_input = true;
                }
            } else {
                // Check if desired is in integer format.
                if (Number.isInteger(desired_hue) && desired_hue >= 0 && desired_hue <= 360) {
                    // Valid hue integer.
                    valid_input = true;
                }
            }
        }

        if (valid_input) {
            // Change hue.
            new_color = old_color.slice();

            if (Array.isArray(desired_hue)) {
                new_color[0] = desired_hue[0];
            } else {
                new_color[0] = desired_hue;
            }
        }

        // Print and return results.
        if (print_result) {
            console.log('[adjust_color_hue] Old: ' + old_color + '   Desired: ' + desired_hue + '   New: ' + new_color);
        }
        return new_color;
    },

    /**
     * Convert arg 1 to match saturation of arg 2.
     */
    adjust_color_saturation: function adjust_color_saturation(old_color, desired_sat) {
        var print_result = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

        var valid_input = false;
        var new_color = null;

        // Validate old color as HSL array.
        if (color_parse.validate_for_HSL(old_color)) {

            // Check if desired is in HSL format.
            if (Array.isArray(desired_sat)) {
                if (color_parse.validate_for_HSL(desired_sat)) {
                    // Valid HSL array.
                    valid_input = true;
                }
            } else {
                // Check if desired is in integer format.
                if (Number.isInteger(desired_sat) && desired_sat >= 0 && desired_sat <= 100) {
                    // Valid hue integer.
                    valid_input = true;
                }
            }
        }

        if (valid_input) {
            // Change saturation.
            new_color = old_color.slice();

            if (Array.isArray(desired_sat)) {
                new_color[1] = desired_sat[1];
            } else {
                new_color[1] = desired_sat;
            }
        }

        // Print and return results.
        if (print_result) {
            console.log('[adjust_color_sat] Old: ' + old_color + '   Desired: ' + desired_sat + '   New: ' + new_color);
        }
        return new_color;
    },

    /**
     * Convert arg 1 to match lightness of arg 2.
     */
    adjust_color_lightness: function adjust_color_lightness(old_color, desired_li) {
        var print_result = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

        var valid_input = false;
        var new_color = null;

        // Validate old color as HSL array.
        if (color_parse.validate_for_HSL(old_color)) {

            // Check if desired is in HSL format.
            if (Array.isArray(desired_li)) {
                if (color_parse.validate_for_HSL(desired_li)) {
                    // Valid HSL array.
                    valid_input = true;
                }
            } else {
                // Check if desired is in integer format.
                if (Number.isInteger(desired_li) && desired_li >= 0 && desired_li <= 100) {
                    // Valid hue integer.
                    valid_input = true;
                }
            }
        }

        if (valid_input) {
            // Change lightness.
            new_color = old_color.slice();

            if (Array.isArray(desired_li)) {
                new_color[2] = desired_li[2];
            } else {
                new_color[2] = desired_li;
            }
        }

        // Print and return results.
        if (print_result) {
            console.log('[adjust_color_light] Old: ' + old_color + '   Desired: ' + desired_li + '   New: ' + new_color);
        }

        return new_color;
    }

    // export {
    //     color_parse,
    //     color_calc,
    // }

};

},{}],2:[function(require,module,exports){
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_adjustment = require('./components/color_adjustment');

var _color_adjustment2 = _interopRequireDefault(_color_adjustment);

var _color_selection = require('./components/color_selection');

var _color_selection2 = _interopRequireDefault(_color_selection);

var _wmu_color_display = require('./components/wmu_color_display');

var _wmu_color_display2 = _interopRequireDefault(_wmu_color_display);

var _color_functions = require('./color_functions');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Color tool.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                *
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Allows easy display of wmu colors, as well as selection and manipulation of current color.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var ColorTool = function (_React$Component) {
    _inherits(ColorTool, _React$Component);

    /**
     * Constructor for component.
     */
    function ColorTool(props) {
        _classCallCheck(this, ColorTool);

        var _this = _possibleConstructorReturn(this, (ColorTool.__proto__ || Object.getPrototypeOf(ColorTool)).call(this, props));

        var hex_value = '#c0c0c0';
        var rgb_value = _color_functions.color_calc.convert_hex_to_rgb(hex_value);
        var hsl_value = _color_functions.color_calc.convert_rgb_to_hsl(rgb_value);

        _this.state = {
            hex_value: hex_value,
            rgb_value: rgb_value,
            hsl_value: hsl_value,
            hex_display: hex_value,
            rgb_display: rgb_value,
            hsl_display: hsl_value
        };

        _this.setColor = _this.setColor.bind(_this);
        _this.handleHexChange = _this.handleHexChange.bind(_this);
        _this.handleRgbChange = _this.handleRgbChange.bind(_this);
        _this.handleHslChange = _this.handleHslChange.bind(_this);
        return _this;
    }

    /**
     * Set color state of topmost parent element.
     */


    _createClass(ColorTool, [{
        key: 'setColor',
        value: function setColor(value) {
            if (_color_functions.color_parse.parse_hex_string(value) != null) {
                var hex_value = value;
                var rgb_value = _color_functions.color_calc.convert_hex_to_rgb(hex_value);
                var hsl_value = _color_functions.color_calc.convert_rgb_to_hsl(rgb_value);

                this.setState({
                    hex_value: hex_value,
                    rgb_value: rgb_value,
                    hsl_value: hsl_value,

                    hex_display: hex_value,
                    rgb_display: rgb_value,
                    hsl_display: hsl_value
                });
            }
        }

        /**
         * Event for changing color with hex syntax.
         */

    }, {
        key: 'handleHexChange',
        value: function handleHexChange(event) {
            // Get and save displayed value.
            var hex_display = event.target.value;
            this.setState({
                hex_display: hex_display
            });

            // Attempt to parse hex value.
            var hex_value = _color_functions.color_parse.parse_hex_string(hex_display);
            if (hex_value != null) {
                this.setColor(hex_value);
            }
        }

        /**
         * Event for changing color with rgb syntax.
         */

    }, {
        key: 'handleRgbChange',
        value: function handleRgbChange(event) {
            // Get and save displayed value.
            var rgb_display = event.target.value;
            this.setState({
                rgb_display: rgb_display
            });

            // Attempt to parse into array. Remove any empty/invalid indexes.
            var rgb_array = rgb_display.split(',');
            for (var index = rgb_array.length - 1; index >= 0; index--) {
                if (rgb_array[index].trim() == '') {
                    rgb_array.splice(index, 1);
                }
            }

            // Check if parsed array is valid.
            if (rgb_array.length == 3) {
                var rgb_value = _color_functions.color_parse.parse_rgb_string(event.target.value);

                if (rgb_value != null) {
                    var hex_value = _color_functions.color_calc.convert_rgb_to_hex(rgb_value);

                    this.setColor(hex_value);
                }
            }
        }

        /**
         * Event for changing color with Hsl syntax.
         */

    }, {
        key: 'handleHslChange',
        value: function handleHslChange(event) {
            // Get and save displayed value.
            var hsl_display = event.target.value;
            this.setState({
                hsl_display: hsl_display
            });

            // Attempt to parse into array. Remove any empty/invalid indexes.
            var hsl_array = hsl_display.split(',');
            for (var index = hsl_array.length - 1; index >= 0; index--) {
                if (hsl_array[index].trim() == '') {
                    hsl_array.splice(index, 1);
                }
            }

            // Check if parsed array is valid.
            if (hsl_array.length == 3) {
                var hsl_value = _color_functions.color_parse.parse_hsl_string(event.target.value);

                if (hsl_value != null) {
                    var rgb_value = _color_functions.color_calc.convert_hsl_to_rgb(hsl_value);
                    var hex_value = _color_functions.color_calc.convert_rgb_to_hex(rgb_value);

                    this.setColor(hex_value);
                }
            }
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'center' },
                React.createElement(_wmu_color_display2.default, { setParentColor: this.setColor }),
                React.createElement(_color_selection2.default, {
                    hex_value: this.state.hex_value,
                    rgb_value: this.state.rgb_value,
                    hsl_value: this.state.hsl_value,
                    hex_display: this.state.hex_display,
                    rgb_display: this.state.rgb_display,
                    hsl_display: this.state.hsl_display,
                    setParentColor: this.setColor,
                    handleHexChange: this.handleHexChange,
                    handleRgbChange: this.handleRgbChange,
                    handleHslChange: this.handleHslChange
                }),
                React.createElement(_color_adjustment2.default, {
                    hex_value: this.state.hex_value,
                    rgb_value: this.state.rgb_value,
                    hsl_value: this.state.hsl_value,
                    setParentColor: this.setColor
                })
            );
        }
    }]);

    return ColorTool;
}(React.Component);

// Start of React logic.


function App() {
    return React.createElement(ColorTool, null);
}

// Render to page.
ReactDOM.render(App(), document.getElementById('react-root'));

},{"./color_functions":1,"./components/color_adjustment":3,"./components/color_selection":6,"./components/wmu_color_display":7}],3:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_display = require('./color_display');

var _color_display2 = _interopRequireDefault(_color_display);

var _color_functions = require('../color_functions');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Rows of Saturation/Lightness adjustement for provided value.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var ColorLine = function (_React$Component) {
    _inherits(ColorLine, _React$Component);

    /**
     * Constructor for component.
     */
    function ColorLine(props) {
        _classCallCheck(this, ColorLine);

        return _possibleConstructorReturn(this, (ColorLine.__proto__ || Object.getPrototypeOf(ColorLine)).call(this, props));
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(ColorLine, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { id: 'color-adjustment' },
                React.createElement(
                    'div',
                    null,
                    React.createElement(_color_display2.default, {
                        title: '0% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 0, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '10% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 10, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '20% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 20, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '30% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 30, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '40% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 40, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '50% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 50, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '60% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 60, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '70% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 70, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '80% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 80, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '90% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 90, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '100% Sat',
                        hsl_value: _color_functions.color_calc.adjust_color_saturation(this.props.hsl_value, [0, 100, 0]),
                        setParentColor: this.props.setParentColor
                    })
                ),
                React.createElement(
                    'div',
                    null,
                    React.createElement(_color_display2.default, {
                        title: '0% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 0]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '10% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 10]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '20% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 20]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '30% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 30]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '40% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 40]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '50% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 50]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '60% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 60]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '70% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 70]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '80% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 80]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '90% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 90]),
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: '100% Light',
                        hsl_value: _color_functions.color_calc.adjust_color_lightness(this.props.hsl_value, [0, 0, 100]),
                        setParentColor: this.props.setParentColor
                    })
                )
            );
        }
    }]);

    return ColorLine;
}(React.Component);

exports.default = ColorLine;

},{"../color_functions":1,"./color_display":4}],4:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_functions = require('../color_functions');

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Displays passed color as swatch and values for hex, rgb, and hsl syntax.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

// import color_calc from '../color_functions';


var ColorDisplay = function (_React$Component) {
    _inherits(ColorDisplay, _React$Component);

    /**
     * Constructor for component.
     */
    function ColorDisplay(props) {
        _classCallCheck(this, ColorDisplay);

        return _possibleConstructorReturn(this, (ColorDisplay.__proto__ || Object.getPrototypeOf(ColorDisplay)).call(this, props));
    }

    /**
     * Hancles click of color swatch.
     */


    _createClass(ColorDisplay, [{
        key: 'handleClick',
        value: function handleClick(hex_value) {
            // console.log('Clicked swatch with value of: ' + hex_value);
            this.props.setParentColor(hex_value);
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: 'render',
        value: function render() {
            var _this2 = this;

            var hex_value = null;
            var rgb_value = null;
            var hsl_value = null;
            var null_value = false;

            // Get state from props.
            if (this.props.hex_value != null) {
                hex_value = this.props.hex_value;
            } else {
                null_value = true;
            }
            if (this.props.rgb_value != null) {
                rgb_value = this.props.rgb_value;
            } else {
                null_value = true;
            }
            if (this.props.hsl_value != null) {
                hsl_value = this.props.hsl_value;
            } else {
                null_value = true;
            }

            // If any of above was null, populate value from what was passed.
            if (null_value) {
                if (hex_value != null) {
                    // Hex was not null.
                    if (rgb_value == null) {
                        rgb_value = _color_functions.color_calc.convert_hex_to_rgb(hex_value);
                    }
                    if (hsl_value == null) {
                        hsl_value = _color_functions.color_calc.convert_rgb_to_hsl(rgb_value);
                    }
                } else if (rgb_value != null) {
                    // Rgb was not null. At least hex was.
                    hex_value = _color_functions.color_calc.convert_rgb_to_hex(rgb_value);
                    if (hsl_value == null) {
                        hsl_value = _color_functions.color_calc.convert_rgb_to_hsl(rgb_value);
                    }
                } else {
                    // Hsl was not null. Other two both were.
                    rgb_value = _color_functions.color_calc.convert_hsl_to_rgb(hsl_value);
                    hex_value = _color_functions.color_calc.convert_rgb_to_hex(rgb_value);
                }
            }

            return React.createElement(
                'div',
                { className: 'color-display' },
                React.createElement(
                    'div',
                    null,
                    React.createElement('div', {
                        className: 'color-box',
                        value: hex_value,
                        style: { backgroundColor: hex_value },
                        onClick: function onClick() {
                            return _this2.handleClick(hex_value);
                        } }),
                    React.createElement(
                        'h5',
                        null,
                        this.props.title
                    )
                ),
                React.createElement(
                    'p',
                    null,
                    'Hex: ',
                    hex_value
                ),
                React.createElement(
                    'p',
                    null,
                    'RGB: ',
                    rgb_value[0],
                    ', ',
                    rgb_value[1],
                    ', ',
                    rgb_value[2]
                ),
                React.createElement(
                    'p',
                    null,
                    'HSL: ',
                    hsl_value[0],
                    ', ',
                    hsl_value[1],
                    ', ',
                    hsl_value[2]
                )
            );
        }
    }]);

    return ColorDisplay;
}(React.Component);

// <div
//                         className='color-box'
//                         value={ hex_value }
//                         style={{ backgroundColor: hex_value }}
//                         onClick={ this.handleClick.bind(this) }>
//                     </div>

exports.default = ColorDisplay;

},{"../color_functions":1}],5:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_functions = require('../color_functions');

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Allows changing of current color through hex, rgb, or hsl syntax.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var ColorEdit = function (_React$Component) {
    _inherits(ColorEdit, _React$Component);

    /**
     * Constructor for component.
     */
    function ColorEdit(props) {
        _classCallCheck(this, ColorEdit);

        return _possibleConstructorReturn(this, (ColorEdit.__proto__ || Object.getPrototypeOf(ColorEdit)).call(this, props));
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(ColorEdit, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'color-edit' },
                React.createElement('div', { className: 'color-box', style: { backgroundColor: this.props.hex_value } }),
                React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'p',
                        null,
                        'Hex Value:'
                    ),
                    React.createElement('input', { type: 'text', value: this.props.hex_display, onChange: this.props.handleHexChange })
                ),
                React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'p',
                        null,
                        'Rgb Value:'
                    ),
                    React.createElement('input', { type: 'text', value: this.props.rgb_display, onChange: this.props.handleRgbChange })
                ),
                React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'p',
                        null,
                        'Hsl Value:'
                    ),
                    React.createElement('input', { type: 'text', value: this.props.hsl_display, onChange: this.props.handleHslChange })
                )
            );
        }
    }]);

    return ColorEdit;
}(React.Component);

exports.default = ColorEdit;

},{"../color_functions":1}],6:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_edit = require('./color_edit');

var _color_edit2 = _interopRequireDefault(_color_edit);

var _color_functions = require('../color_functions');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Component to allow selection of current color.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var ColorSelection = function (_React$Component) {
    _inherits(ColorSelection, _React$Component);

    /**
     * Constructor for component.
     */
    function ColorSelection(props) {
        _classCallCheck(this, ColorSelection);

        var _this = _possibleConstructorReturn(this, (ColorSelection.__proto__ || Object.getPrototypeOf(ColorSelection)).call(this, props));

        ;
        return _this;
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(ColorSelection, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { id: 'color-selection' },
                React.createElement(_color_edit2.default, {
                    title: 'Primary',
                    hex_value: this.props.hex_value,
                    rgb_value: this.props.rgb_value,
                    hsl_value: this.props.hsl_value,
                    hex_display: this.props.hex_display,
                    rgb_display: this.props.rgb_display,
                    hsl_display: this.props.hsl_display,
                    setParentColor: this.props.setParentColor,
                    handleHexChange: this.props.handleHexChange,
                    handleRgbChange: this.props.handleRgbChange,
                    handleHslChange: this.props.handleHslChange
                })
            );
        }
    }]);

    return ColorSelection;
}(React.Component);

exports.default = ColorSelection;

},{"../color_functions":1,"./color_edit":5}],7:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _color_display = require('./color_display');

var _color_display2 = _interopRequireDefault(_color_display);

var _color_functions = require('../color_functions');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Displays all wmu colors, both official and used on the main campus website.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var WmuColorDisplay = function (_React$Component) {
    _inherits(WmuColorDisplay, _React$Component);

    /**
     * Constructor for component.
     */
    function WmuColorDisplay(props) {
        _classCallCheck(this, WmuColorDisplay);

        return _possibleConstructorReturn(this, (WmuColorDisplay.__proto__ || Object.getPrototypeOf(WmuColorDisplay)).call(this, props));
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(WmuColorDisplay, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { id: 'wmu-color-display' },
                React.createElement(
                    'div',
                    null,
                    React.createElement(_color_display2.default, {
                        title: 'WMU Primary Gold',
                        hex_value: '#ffae00',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Primary Brown',
                        hex_value: '#442416',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement('br', null),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Secondary Chocolate',
                        hex_value: '#7c5826',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Secondary Khaki',
                        hex_value: '#c0aa71',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Secondary Sienna',
                        hex_value: '#a9431e',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Secondary Tangerine',
                        hex_value: '#d87c21',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Secondary Light Tan',
                        hex_value: '#ede1aa',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement('br', null),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Teal',
                        hex_value: '#0b645d',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Red',
                        hex_value: '#b91233',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Plum',
                        hex_value: '#865f7f',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Sky Blue',
                        hex_value: '#0091c1',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Green Apple',
                        hex_value: '#7ab700',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Dark Grey',
                        hex_value: '#816f5f',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Warm Grey',
                        hex_value: '#bdb1a7',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Metallic Gold',
                        hex_value: '#8b6f4e',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Metallic Brown',
                        hex_value: '#594839',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Accent Metallic Silver',
                        hex_value: '#8a8d8f',
                        setParentColor: this.props.setParentColor
                    })
                ),
                React.createElement(
                    'div',
                    null,
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Gold',
                        hex_value: '#fcc30f',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Brown',
                        hex_value: '#986516',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Header',
                        hex_value: '#331900',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Header Alt',
                        hex_value: '#c48b04',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Header Alt Text',
                        hex_value: '#fde392',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Infographic Grey',
                        hex_value: '#333333',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Infographic Header',
                        hex_value: '#cccccc',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Infographic Text',
                        hex_value: '#999999',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Sidebar',
                        hex_value: '#eedab9',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement('br', null),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Info',
                        hex_value: '#1abee9',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Info Hover',
                        hex_value: '#129abd',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Success',
                        hex_value: '#7ea634',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Success Hover',
                        hex_value: '#65852a',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Warn',
                        hex_value: '#ef8843',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Warn Hover',
                        hex_value: '#e26613',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Error',
                        hex_value: '#c30a0a',
                        setParentColor: this.props.setParentColor
                    }),
                    React.createElement(_color_display2.default, {
                        title: 'WMU Web Error Hover',
                        hex_value: '#9c0808',
                        setParentColor: this.props.setParentColor
                    })
                )
            );
        }
    }]);

    return WmuColorDisplay;
}(React.Component);

exports.default = WmuColorDisplay;

},{"../color_functions":1,"./color_display":4}]},{},[2]);
