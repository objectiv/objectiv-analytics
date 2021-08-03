import React from 'react';
import Button from "./Button";
import detectPosition from "./detectPosition";
import { usePositionContext } from "./PositionProvider";

function Box(props:any) {
  const { setPosition } = usePositionContext();
  // @ts-ignore
  console.log(props)

  if (!setPosition) {
    return <>loading...</>;
  }

  return <div style={{padding: 10, border: 1, borderColor: 'black', borderStyle: 'solid', display: 'inline-block'}}>
    <h2>Box Component</h2>
    <p>
      <Button>Button Component in Box Component</Button>
    </p>
    <p>
      <button
        onClick={
          async () => {
            const position = await detectPosition()
            setPosition(position);
          }
        }
      >Inline &lt;button&gt; in Box Component</button>
    </p>
  </div>
}

export default Box;
