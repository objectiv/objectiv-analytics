import React, { CSSProperties } from 'react';
import ButtonComponent from './ButtonComponent';
import detectPosition from './detectPosition';
import { ContextType, trackElement } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const boxStyle = (color: string): CSSProperties => ({
  margin: 10,
  padding: 10,
  width: 180,
  height: 180,
  borderRadius: '50%',
  border: 1,
  borderColor: 'black',
  borderStyle: 'solid',
  display: 'inline-flex',
  flexDirection: 'column',
  backgroundColor: color,
  alignItems: 'center',
});

function CircleComponent({ id, color }: { id: string; color: string }) {
  const { setElementContext } = useElementContext();

  return (
    <div {...trackElement(id)} style={boxStyle(color)}>
      <h2 style={{ margin: 5 }}>Circle</h2>
      <h4>named function</h4>
      <ButtonComponent id="button-component">Button Component</ButtonComponent>
      <br />
      <button
        {...trackElement('inline-button', ContextType.button)}
        onClick={async ({ target }) => {
          const position = await detectPosition(target);
          setElementContext(position);
        }}
      >
        &lt;button&gt; Tag
      </button>
      <br />
    </div>
  );
}

export default CircleComponent;
