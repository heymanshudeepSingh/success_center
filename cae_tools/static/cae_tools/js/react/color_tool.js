/**
 * Color tool.
 *
 * Allows easy display of wmu colors, as well as selection and manipulation of current color.
 */


import ColorAdjustment from './components/color_adjustment';
import ColorSelection from './components/color_selection';
import WmuColorDisplay from './components/wmu_color_display';

import { color_calc, color_parse } from './color_functions';


class ColorTool extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        var hex_value = '#c0c0c0';
        var rgb_value = color_calc.convert_hex_to_rgb(hex_value);
        var hsl_value = color_calc.convert_rgb_to_hsl(rgb_value);

        this.state = {
            hex_value: hex_value,
            rgb_value: rgb_value,
            hsl_value: hsl_value,
            hex_display: hex_value,
            rgb_display: rgb_value,
            hsl_display: hsl_value,
        };

        this.setColor = this.setColor.bind(this);
        this.handleHexChange = this.handleHexChange.bind(this);
        this.handleRgbChange = this.handleRgbChange.bind(this);
        this.handleHslChange = this.handleHslChange.bind(this);
    }


    /**
     * Set color state of topmost parent element.
     */
    setColor(value) {
        if (color_parse.parse_hex_string(value) != null) {
            var hex_value = value;
            var rgb_value = color_calc.convert_hex_to_rgb(hex_value);
            var hsl_value = color_calc.convert_rgb_to_hsl(rgb_value);

            this.setState({
                hex_value: hex_value,
                rgb_value: rgb_value,
                hsl_value: hsl_value,

                hex_display: hex_value,
                rgb_display: rgb_value,
                hsl_display: hsl_value,
            });
        }
    }


    /**
     * Event for changing color with hex syntax.
     */
    handleHexChange(event) {
        // Get and save displayed value.
        var hex_display = event.target.value;
        this.setState({
            hex_display: hex_display,
        });

        // Attempt to parse hex value.
        var hex_value = color_parse.parse_hex_string(hex_display);
        if (hex_value != null) {
            this.setColor(hex_value);
        }
    }


    /**
     * Event for changing color with rgb syntax.
     */
    handleRgbChange(event) {
        // Get and save displayed value.
        var rgb_display = event.target.value;
        this.setState({
            rgb_display: rgb_display,
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
            var rgb_value = color_parse.parse_rgb_string(event.target.value);

            if (rgb_value != null) {
                var hex_value = color_calc.convert_rgb_to_hex(rgb_value);

                this.setColor(hex_value);
            }
        }
    }


    /**
     * Event for changing color with Hsl syntax.
     */
    handleHslChange(event) {
        // Get and save displayed value.
        var hsl_display = event.target.value;
        this.setState({
            hsl_display: hsl_display,
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
            var hsl_value = color_parse.parse_hsl_string(event.target.value);

            if (hsl_value != null) {
                var rgb_value = color_calc.convert_hsl_to_rgb(hsl_value);
                var hex_value = color_calc.convert_rgb_to_hex(rgb_value);

                this.setColor(hex_value);
            }
        }
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        return (
            <div className='center'>
                <WmuColorDisplay setParentColor={ this.setColor } />
                <ColorSelection
                    hex_value={ this.state.hex_value }
                    rgb_value={ this.state.rgb_value }
                    hsl_value={ this.state.hsl_value }
                    hex_display={ this.state.hex_display }
                    rgb_display={ this.state.rgb_display }
                    hsl_display={ this.state.hsl_display }
                    setParentColor={ this.setColor }
                    handleHexChange={ this.handleHexChange }
                    handleRgbChange={ this.handleRgbChange }
                    handleHslChange={ this.handleHslChange }
                />
                <ColorAdjustment
                    hex_value={ this.state.hex_value }
                    rgb_value={ this.state.rgb_value }
                    hsl_value={ this.state.hsl_value }
                    setParentColor={ this.setColor }
                />
            </div>
        )
    }
}


// Start of React logic.
function App() {
    return (
        <ColorTool />
    );
}


// Render to page.
ReactDOM.render(
    App(),
    document.getElementById('react-root')
);
