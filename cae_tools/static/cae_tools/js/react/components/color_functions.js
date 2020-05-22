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


export const color_parse = {

    /**
     * Parses a hex string for validity..
     * :return: A valid hex string, or Null if value was invalid.
     */
    parse_hex_string: function(hex_value) {

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

                    if ((char_value >= 48) && (char_value <= 57)) {
                        valid_char = true;
                    } else if ((char_value >= 65) || (char_value <= 70)) {
                        valid_char = true;
                    } else if ((char_value >= 97) || (char_value <= 102)) {
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
    parse_rgb_string: function(rgb_value) {

        // Check if value is string or already parsed as array.
        if (Array.isArray(rgb_value)) {
            // Found array.
            var rgb_array = rgb_value;
        } else {
            // Found string. Split to array.
            if (rgb_value[0] == '(') {
                // Encased in parenthesis.
                var rgb_array = rgb_value.substring(4, rgb_value.length-1).split(', ').map(Number);

                // Try again if no spaces were present.
                if (rgb_array.length == 1) {
                    rgb_array = rgb_value.substring(4, rgb_value.length-1).split(',').map(Number);
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
            if ((!Number.isInteger(rgb_array[0])) || (rgb_array[0] < 0) || (rgb_array[0] > 255) ||
                (!Number.isInteger(rgb_array[0])) || (rgb_array[1] < 0) || (rgb_array[1] > 255) ||
                (!Number.isInteger(rgb_array[0])) || (rgb_array[2] < 0) || (rgb_array[2] > 255)) {
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
    parse_hsl_string: function(hsl_value) {

        // Check if value is string or already parsed as array.
        if (Array.isArray(hsl_value)) {
            // Found array.
            var hsl_array = hsl_value;
        } else {
            if (hsl_value[0] == '(') {
                // Found string. Split to array.
                var hsl_array = hsl_value.substring(4, hsl_value.length-1).split(', ').map(Number);

                // Try again if no spaces were present.
                if (hsl_array.length == 1) {
                    hsl_array = hsl_value.substring(4, hsl_value.length-1).split(',').map(Number);
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
            if ((!Number.isInteger(hsl_array[0])) || (hsl_array[0] < 0) || (hsl_array[0] > 360) ||
                (!Number.isInteger(hsl_array[0])) || (hsl_array[1] < 0) || (hsl_array[1] > 100) ||
                (!Number.isInteger(hsl_array[0])) || (hsl_array[2] < 0) || (hsl_array[2] > 100)) {
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
    validate_for_HSL: function(value) {

        // Check that value is array.
        if (Array.isArray(value)) {
            // Check that array is exactly 3 elements long.
            if (value.length != 3) {
                console.warn('Invalid HSL array passed: ' + value)
                return false;
            }
        } else {
            console.warn('Expected array of HSL format. Instead got: ' + value);
            return false;
        }

        return true;
    },
}


export const color_calc = {

    /**
     * Converts values from hex (#xxyyzz) to rgb (x, y, z).
     */
    convert_hex_to_rgb: function(hex_value, print_result=false) {

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
    convert_rgb_to_hex: function(rgb_value, print_result=false) {

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
    convert_rgb_to_hsl: function(rgb_value, print_result=false) {

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
    convert_hsl_to_rgb: function(hsl_value, print_result=false) {

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
            function hue2rgb(p, q, t) {
              if (t < 0) t += 1;
              if (t > 1) t -= 1;
              if (t < 1/6) return p + (q - p) * 6 * t;
              if (t < 1/2) return q;
              if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
              return p;
            }

            var q = lightness < 0.5 ? lightness * (1 + saturation) : lightness + saturation - lightness * saturation;
            var p = 2 * lightness - q;

            var red = hue2rgb(p, q, hue + 1/3);
            var green = hue2rgb(p, q, hue);
            var blue = hue2rgb(p, q, hue - 1/3);
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
    convert_hex_to_hsl: function(hex_value, print_result=false) {

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
    convert_hsl_to_hex: function(hsl_value, print_result=false) {

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
    adjust_color_hue: function(old_color, desired_hue, print_result=false) {
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
                if ((Number.isInteger(desired_hue)) && (desired_hue >= 0) && (desired_hue <= 360)) {
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
    adjust_color_saturation: function(old_color, desired_sat, print_result=false) {
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
                if ((Number.isInteger(desired_sat)) && (desired_sat >= 0) && (desired_sat <= 100)) {
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
    adjust_color_lightness: function(old_color, desired_li, print_result=false) {
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
                if ((Number.isInteger(desired_li)) && (desired_li >= 0) && (desired_li <= 100)) {
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
    },

}


// export {
//     color_parse,
//     color_calc,
// }
