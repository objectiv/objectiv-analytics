import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from "./detectPosition";
import { usePositionContext } from "./PositionProvider";
import { tracker } from './tracker';

function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { setPosition } = usePositionContext();

  return setPosition ?
    <tracker.button
      id='button-component'
      onClick={
        async () => {
          const position = await detectPosition()
          setPosition(position);
        }
      }
      {...props}
    >{props.children}</tracker.button> : null;
}

export default Button;
