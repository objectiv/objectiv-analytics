/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeOverlayContext } from '../common/factories/makeOverlayContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of OverlayContextWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type OverlayContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in an OverlayContext.
 */
export const OverlayContextWrapper = ({ children, id }: OverlayContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeOverlayContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
