import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from './detectPosition';
import { useElementContext } from './TrackerElementContextProvider';
import { ContextType, trackElement } from './tracker';

function ButtonComponent({ id, ...otherProps }: ButtonHTMLAttributes<HTMLButtonElement> & { id: string }) {
  const { setElementContext } = useElementContext();

  return (
    <button
      {...trackElement(id, ContextType.button)}
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
