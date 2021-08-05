import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from './detectPosition';
import { useElementContext } from './TrackerElementContextProvider';
import { tracker } from './tracker';

function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { setElementContext } = useElementContext();

  return (
    <tracker.button
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
    </tracker.button>
  );
}

export default Button;
