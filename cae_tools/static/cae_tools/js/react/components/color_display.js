/**
 * Displays passed color as swatch and values for hex, rgb, and hsl syntax.
 */


// import color_calc from '../color_functions';
import { color_calc } from '../color_functions';


class ColorDisplay extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);
    }


    /**
     * Hancles click of color swatch.
     */
    handleClick(hex_value) {
        // console.log('Clicked swatch with value of: ' + hex_value);
        this.props.setParentColor(hex_value);
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
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
                    rgb_value = color_calc.convert_hex_to_rgb(hex_value);
                }
                if (hsl_value == null) {
                    hsl_value = color_calc.convert_rgb_to_hsl(rgb_value);
                }
            } else if (rgb_value != null) {
                // Rgb was not null. At least hex was.
                hex_value = color_calc.convert_rgb_to_hex(rgb_value);
                if (hsl_value == null) {
                    hsl_value = color_calc.convert_rgb_to_hsl(rgb_value);
                }
            } else {
                // Hsl was not null. Other two both were.
                rgb_value = color_calc.convert_hsl_to_rgb(hsl_value);
                hex_value = color_calc.convert_rgb_to_hex(rgb_value);
            }
        }

        return (
            <div className='color-display'>
                <div>
                    <div
                        className='color-box'
                        value={ hex_value }
                        style={{ backgroundColor: hex_value }}
                        onClick={ () => this.handleClick(hex_value) }>
                    </div>
                    <h5>{ this.props.title }</h5>
                </div>
                <p>Hex: { hex_value }</p>
                <p>RGB: { rgb_value[0] }, { rgb_value[1] }, { rgb_value[2] }</p>
                <p>HSL: { hsl_value[0] }, { hsl_value[1] }, { hsl_value[2] }</p>
            </div>
        )
    }
}


// <div
//                         className='color-box'
//                         value={ hex_value }
//                         style={{ backgroundColor: hex_value }}
//                         onClick={ this.handleClick.bind(this) }>
//                     </div>

export default ColorDisplay;
