import { createElement, FC } from 'react';

const OBJT_PREFIX = 'objt';
const OBJT_NAME_SEPARATOR = '-';
const OBJT_VALUE_SEPARATOR = ':';
const OBJT_LOCATION = `${OBJT_PREFIX}${OBJT_NAME_SEPARATOR}location`;

enum ElementType {
  div = 'div',
  span = 'span',
  button = 'button'
}

const contextTypeByElementType: {[key in ElementType]: string} = {
  [ElementType.div]: 'section',
  [ElementType.span]: 'section',
  [ElementType.button]: 'button',
}

type ReactHTMLProperties = React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
type CommonContextProperties = ReactHTMLProperties & {
  id: string,
}

const ContextFactory: (elementType: ElementType) => FC<CommonContextProperties> = (elementType) => (props) => {
  const objectivContextType = contextTypeByElementType[elementType];
  const { id, ...otherProps } = props;
  const location = `${objectivContextType}${OBJT_VALUE_SEPARATOR}${id}`;

  return createElement(
    elementType, {
      ...otherProps,
      [OBJT_LOCATION]: location,
    }
  )
}

export const tracker = new Proxy(ElementType, {
  get(_, elementType: ElementType) {
    return ContextFactory(elementType)
  }
})
