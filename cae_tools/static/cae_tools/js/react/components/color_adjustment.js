/**
 * Rows of Saturation/Lightness adjustement for provided value.
 */


import ColorDisplay from './color_display';

import { color_calc } from '../color_functions';


class ColorLine extends React.Component {

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
            <div id='color-adjustment'>
                <div>
                    <ColorDisplay
                        title='0% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,0,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='10% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,10,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='20% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,20,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='30% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,30,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='40% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,40,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='50% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,50,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='60% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,60,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='70% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,70,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='80% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,80,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='90% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,90,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='100% Sat'
                        hsl_value={ color_calc.adjust_color_saturation(this.props.hsl_value, [0,100,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                </div>
                <div>
                    <ColorDisplay
                        title='0% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,0]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='10% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,10]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='20% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,20]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='30% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,30]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='40% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,40]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='50% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,50]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='60% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,60]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='70% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,70]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='80% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,80]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='90% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,90]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title='100% Light'
                        hsl_value={ color_calc.adjust_color_lightness(this.props.hsl_value, [0,0,100]) }
                        setParentColor ={ this.props.setParentColor }
                    />
                </div>
            </div>
        )
    }
}






export default ColorLine;
