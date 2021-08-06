import React, { CSSProperties, FC } from 'react';
import ButtonComponent from './ButtonComponent';
import detectPosition from './detectPosition';
import { trackButton, trackDiv } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const boxStyle = (color: string): CSSProperties => ({
  margin: 10,
  padding: 10,
  border: 1,
  borderColor: 'black',
  borderStyle: 'solid',
  display: 'inline-flex',
  flexDirection: 'column',
  backgroundColor: color,
  alignItems: 'center',
});

const BoxComponent: FC<{ id: string; color: string }> = ({ children, id, color }) => {
  const { setElementContext } = useElementContext();

  return (
    <div {...trackDiv(id)} style={boxStyle(color)}>
      <h2 style={{ margin: 5 }}>Box</h2>
      <h4>anonymous arrow function</h4>
      <ButtonComponent id="button-component">Button Component</ButtonComponent>
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
      {children}
    </div>
  );
};

export default BoxComponent;
