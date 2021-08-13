import React, { CSSProperties } from 'react';
import ButtonComponent from './ButtonComponent';
import detectPosition from './detectPosition';
import { trackButton, trackElement } from './tracker';
import { TrackerElementContext } from './TrackerElementContextProvider';

const boxStyle = (color: string): CSSProperties => ({
  margin: 10,
  padding: 10,
  minWidth: 180,
  borderRadius: '25%',
  border: 1,
  borderColor: 'black',
  borderStyle: 'solid',
  display: 'inline-flex',
  flexDirection: 'column',
  backgroundColor: color,
  alignItems: 'center',
});

class RoundedBoxComponent extends React.Component<{ id: string; color: string }> {
  static contextType = TrackerElementContext;

  render() {
    return (
      <div {...trackElement(this.props.id)} style={boxStyle(this.props.color)}>
        <h2 style={{ margin: 5 }}>Rounded Box</h2>
        <h4>class component</h4>
        <ButtonComponent id="button-component">Button Component</ButtonComponent>
        <br />
        <button
          {...trackButton('inline-button')}
          onClick={async ({ target }) => {
            const position = await detectPosition(target);
            this.context.setElementContext(position);
          }}
        >
          &lt;button&gt; Tag
        </button>
        <br />
        {this.props.children}
      </div>
    );
  }
}

export default RoundedBoxComponent;
