/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeInputContext } from '../common/factories/makeInputContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of InputContextWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type InputContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in a InputContext.
 */
export const InputContextWrapper = ({ children, id }: InputContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeInputContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
