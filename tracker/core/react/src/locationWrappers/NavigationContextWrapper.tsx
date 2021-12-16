/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeNavigationContext } from '../common/factories/makeNavigationContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of NavigationContextWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type NavigationContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in a NavigationContext.
 */
export const NavigationContextWrapper = ({ children, id }: NavigationContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeNavigationContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
