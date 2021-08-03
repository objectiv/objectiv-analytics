import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from "./detectPosition";
import { usePositionContext } from "./PositionProvider";

function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { setPosition } = usePositionContext();

  return setPosition ?
    <button
      onClick={
        async () => {
          const position = await detectPosition()
          setPosition(position);
        }
      }
      {...props}
    >{props.children}</button> : null;
}

export default Button;
