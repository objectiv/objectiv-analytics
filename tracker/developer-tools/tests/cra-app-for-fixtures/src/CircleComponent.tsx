import React, { CSSProperties } from 'react';
import ButtonComponent from './ButtonComponent';
import detectPosition from './detectPosition';
import { trackButton, trackDiv } from './tracker';
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
  alignItems: 'center'
});

function CircleComponent({ id, color }: { id: string; color: string }) {
  const { setElementContext } = useElementContext();

  return (
    <div {...trackDiv(id)} style={boxStyle(color)}>
      <h2 style={{ margin: 5 }}>Circle</h2>
      <h4>named function</h4>
      <ButtonComponent>Button Component</ButtonComponent>
      <br />
      <button
        {...trackButton('inline-button')}
        onClick={async ({ target }) => {
          if (!target || !(target instanceof HTMLElement)) {
            return;
          }
          const elementId = target.dataset.objectiv;
          if (!elementId) {
            return;
          }
          const position = await detectPosition(elementId);
          setElementContext(position);
        }}
      >
        &lt;button&gt; Tag
      </button>
      <br />
    </div>
  );
};

export default CircleComponent;
