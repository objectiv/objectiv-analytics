/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeActionContext } from '../common/factories/makeActionContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of ActionContextWrapper.
 */
export type ActionContextWrapperProps = SectionContextWrapperProps & {
  /**
   * A description of what the action is about.
   */
  text: string;
};

/**
 * Wraps its children in an ActionContext.
 */
export const ActionContextWrapper = ({ children, id, text }: ActionContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeActionContext({ id, text })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
