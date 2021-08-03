import React from 'react';
import Button from "./Button";
import detectPosition from "./detectPosition";
import { usePositionContext } from "./PositionProvider";
import { tracker } from './tracker';

const boxStyle = {
  padding: 10,
  border: 1,
  borderColor: 'black',
  borderStyle: 'solid',
  display: 'inline-block'
};

function Box(props:any) {
  const { setPosition } = usePositionContext();
  // @ts-ignore
  console.log(props)

  if (!setPosition) {
    return <>loading...</>;
  }

  return <tracker.div id='box' style={boxStyle}>
    <h2>Box Component</h2>
    <p>
      <Button>Button Component in Box Component</Button>
    </p>
    <p>
      <tracker.button id='inline-button'
        onClick={
          async () => {
            const position = await detectPosition()
            setPosition(position);
          }
        }
      >Inline &lt;button&gt; in Box Component</tracker.button>
    </p>
  </tracker.div>
}

export default Box;
