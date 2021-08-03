import { createElement, FC } from 'react';

const OBJT_PREFIX = 'objt';
const OBJT_NAME_SEPARATOR = '-';
const OBJT_VALUE_SEPARATOR = ':';
const OBJT_LOCATION = `${OBJT_PREFIX}${OBJT_NAME_SEPARATOR}location`;

// TODO get this from Schema._context_type literals
enum ContextType {
  section = 'SectionContext',
  button = 'ButtonContext',
}

type JSXElements = keyof JSX.IntrinsicElements;
type ReactHTMLProps = React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
type ContextElementProps = ReactHTMLProps & {
  id: string,
}

const ContextElementFactory: (elementType: JSXElements, contextType: ContextType) => FC<ContextElementProps> = (elementType, contextType) => (props) => {
  const { id, ...otherProps } = props;
  const location = `${contextType}${OBJT_VALUE_SEPARATOR}${id}`;

  return createElement(
    elementType, {
      ...otherProps,
      [OBJT_LOCATION]: location,
    }
  )
}

export const TrackerButton = ContextElementFactory('button', ContextType.button)
export const TrackerDiv = ContextElementFactory('div', ContextType.section)
export const TrackerSpan = ContextElementFactory('span', ContextType.section)

export const tracker = {
  button: TrackerButton,
  div: TrackerDiv,
  span: TrackerSpan
}
