import React, { CSSProperties, ReactNode } from 'react';
import ButtonComponent from './ButtonComponent';
import detectPosition from './detectPosition';
import { trackButton, trackDiv } from './tracker';
import { useElementContext } from './TrackerElementContextProvider';

const boxStyle = (color: string): CSSProperties => ({
  margin: 10,
  padding: 10,
  border: 10,
  borderColor: 'black',
  borderStyle: 'solid',
  display: 'inline-flex',
  flexDirection: 'column',
  backgroundColor: color,
  alignItems: 'center',
});

// eslint-disable-next-line import/no-anonymous-default-export
export default ({ children, id, color }: { children?: ReactNode; id: string; color: string }) => {
  const { setElementContext } = useElementContext();

  return (
    <div {...trackDiv(id)} style={boxStyle(color)}>
      <h2 style={{ margin: 5 }}>Box</h2>
      <h4>export default anonymous arrow function</h4>
      <ButtonComponent id="button-component">Button Component</ButtonComponent>
      <br />
      <button
        {...trackButton('inline-button')}
        onClick={async ({ target }) => {
          const position = await detectPosition(target);
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
