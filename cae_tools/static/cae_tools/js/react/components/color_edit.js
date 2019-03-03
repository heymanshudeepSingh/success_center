/**
 * Allows changing of current color through hex, rgb, or hsl syntax.
 */


import { color_calc, color_parse } from '../color_functions';


class ColorEdit extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        return (
            <div className='color-edit'>
                <div className="color-box" style={{ backgroundColor: this.props.hex_value }}></div>
                <div>
                    <p>Hex Value:</p>
                    <input type='text' value={ this.props.hex_display } onChange={ this.props.handleHexChange } />
                </div>
                <div>
                    <p>Rgb Value:</p>
                    <input type='text' value={ this.props.rgb_display } onChange={ this.props.handleRgbChange } />
                </div>
                <div>
                    <p>Hsl Value:</p>
                    <input type='text' value={ this.props.hsl_display } onChange={ this.props.handleHslChange } />
                </div>
            </div>
        )
    }
}


export default ColorEdit;
