import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from './detectPosition';
import { useElementContext } from './TrackerElementContextProvider';
import { trackButton } from './tracker';

function ButtonComponent({ id, ...otherProps }: ButtonHTMLAttributes<HTMLButtonElement> & { id: string }) {
  const { setElementContext } = useElementContext();

  return (
    <button
      {...trackButton(id)}
      onClick={async ({ target }) => {
        const position = await detectPosition(target);
        setElementContext(position);
      }}
      {...otherProps}
    >
      {otherProps.children}
    </button>
  );
}

export default ButtonComponent;
