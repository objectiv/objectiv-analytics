import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from './detectPosition';
import { useElementContext } from './TrackerElementContextProvider';
import { trackDiv } from './tracker';

function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { setElementContext } = useElementContext();

  return (
    <button
      {...trackDiv(props.id ?? 'button-component')}
      id={props.id ?? 'button-component'}
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
      {...props}
    >
      {props.children}
    </button>
  );
}

export default Button;
