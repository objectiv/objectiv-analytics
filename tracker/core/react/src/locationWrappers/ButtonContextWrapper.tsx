/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeButtonContext } from '../common/factories/makeButtonContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

export type ButtonContextWrapperProps = SectionContextWrapperProps & {
  /**
   * The label / title of the Button or a description of what it is about.
   */
  text: string;
};

/**
 * Wraps its children in a ButtonContext.
 */
export const ButtonContextWrapper = ({ children, id, text }: ButtonContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeButtonContext({ id, text })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
