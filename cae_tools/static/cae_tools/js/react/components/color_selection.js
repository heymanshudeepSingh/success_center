/**
 * Component to allow selection of current color.
 */


import ColorEdit from './color_edit';

import { color_calc } from '../color_functions';


class ColorSelection extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);;
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        return (
            <div id='color-selection'>
                <ColorEdit
                    title='Primary'
                    hex_value={ this.props.hex_value }
                    rgb_value={ this.props.rgb_value }
                    hsl_value={ this.props.hsl_value }
                    hex_display={ this.props.hex_display }
                    rgb_display={ this.props.rgb_display }
                    hsl_display={ this.props.hsl_display }
                    setParentColor={ this.props.setParentColor }
                    handleHexChange={ this.props.handleHexChange }
                    handleRgbChange={ this.props.handleRgbChange }
                    handleHslChange={ this.props.handleHslChange }
                />
            </div>
        )
    }
}

export default ColorSelection;
