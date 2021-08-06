import React, { ButtonHTMLAttributes } from 'react';
import detectPosition from './detectPosition';
import { useElementContext } from './TrackerElementContextProvider';
import { trackButton } from './tracker';

function ButtonComponent(props: ButtonHTMLAttributes<HTMLButtonElement> & { id: string }) {
  const { setElementContext } = useElementContext();

  return (
    <button
      {...trackButton(props.id)}
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

export default ButtonComponent;
