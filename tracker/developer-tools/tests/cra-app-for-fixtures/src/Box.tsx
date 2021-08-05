import React, { CSSProperties, FC } from 'react';
import Button from './Button';
import detectPosition from './detectPosition';
import { tracker } from './tracker';
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
});

const Box: FC<{ color: string }> = ({ children, color }) => {
  const { setElementContext } = useElementContext();

  return (
    <tracker.div id="box" style={boxStyle(color)}>
      <h2 style={{ margin: 5 }}>Box Component</h2>
      <Button>Button Component</Button>
      <br />
      <tracker.button
        id="inline-button"
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
      </tracker.button>
      <br />
      {children}
    </tracker.div>
  );
};

export default Box;
