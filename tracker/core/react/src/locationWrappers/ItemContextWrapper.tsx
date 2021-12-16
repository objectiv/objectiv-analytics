/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeItemContext } from '../common/factories/makeItemContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of ItemContextWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type ItemContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in an ItemContext.
 */
export const ItemContextWrapper = ({ children, id }: ItemContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeItemContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
