import React, { CSSProperties, FC, ReactNode } from 'react';

const boxStyle = (): CSSProperties => ({
  margin: 10,
  padding: 10,
  border: 2,
  borderColor: 'black',
  borderStyle: 'dashed',
  display: 'inline-flex',
  flexDirection: 'column',
  backgroundColor: 'darkkhaki',
  alignItems: 'center',
});

const ThirdPartyComponent: FC<{ button1: ReactNode; button2: ReactNode }> = ({ button1, button2 }) => {
  return (
    <div style={boxStyle()}>
      <h2 style={{ margin: 0, fontSize: 36 }}>☹☹☹</h2>
      <h4>3rd party component</h4>
      {button1}
      <br />
      {button2}
    </div>
  );
};

export default ThirdPartyComponent;
