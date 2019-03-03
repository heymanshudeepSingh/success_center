/**
 * Displays all wmu colors, both official and used on the main campus website.
 */


import ColorDisplay from './color_display';

import { color_calc } from '../color_functions';


class WmuColorDisplay extends React.Component {

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
            <div id='wmu-color-display'>
                <div>
                    <ColorDisplay
                        title={ 'WMU Primary Gold' }
                        hex_value={ '#ffae00' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Primary Brown' }
                        hex_value={ '#442416' }
                        setParentColor={ this.props.setParentColor }
                    />

                    <br />

                    <ColorDisplay
                        title={ 'WMU Secondary Chocolate' }
                        hex_value={ '#7c5826' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Secondary Khaki' }
                        hex_value={ '#c0aa71' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Secondary Sienna' }
                        hex_value={ '#a9431e' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Secondary Tangerine' }
                        hex_value={ '#d87c21' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Secondary Light Tan' }
                        hex_value={ '#ede1aa' }
                        setParentColor={ this.props.setParentColor }
                    />

                    <br />

                    <ColorDisplay
                        title={ 'WMU Accent Teal' }
                        hex_value={ '#0b645d' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Red' }
                        hex_value={ '#b91233' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Plum' }
                        hex_value={ '#865f7f' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Sky Blue' }
                        hex_value={ '#0091c1' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Green Apple' }
                        hex_value={ '#7ab700' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Dark Grey' }
                        hex_value={ '#816f5f' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Warm Grey' }
                        hex_value={ '#bdb1a7' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Metallic Gold' }
                        hex_value={ '#8b6f4e' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Metallic Brown' }
                        hex_value={ '#594839' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Accent Metallic Silver' }
                        hex_value={ '#8a8d8f' }
                        setParentColor={ this.props.setParentColor }
                    />
                </div>
                <div>
                    <ColorDisplay
                        title={ 'WMU Web Gold' }
                        hex_value={ '#fcc30f' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Brown' }
                        hex_value={ '#986516' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Header' }
                        hex_value={ '#331900' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Header Alt' }
                        hex_value={ '#c48b04' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Header Alt Text' }
                        hex_value={ '#fde392' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Infographic Grey' }
                        hex_value={ '#333333' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Infographic Header' }
                        hex_value={ '#cccccc' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Infographic Text' }
                        hex_value={ '#999999' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Sidebar' }
                        hex_value={ '#eedab9' }
                        setParentColor={ this.props.setParentColor }
                    />

                    <br />

                    <ColorDisplay
                        title={ 'WMU Web Info' }
                        hex_value={ '#1abee9' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Info Hover' }
                        hex_value={ '#129abd' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Success' }
                        hex_value={ '#7ea634' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Success Hover' }
                        hex_value={ '#65852a' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Warn' }
                        hex_value={ '#ef8843' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Warn Hover' }
                        hex_value={ '#e26613' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Error' }
                        hex_value={ '#c30a0a' }
                        setParentColor={ this.props.setParentColor }
                    />
                    <ColorDisplay
                        title={ 'WMU Web Error Hover' }
                        hex_value={ '#9c0808' }
                        setParentColor={ this.props.setParentColor }
                    />
                </div>
            </div>
        )
    }
}


export default WmuColorDisplay;
