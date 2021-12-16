/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeExpandableSectionContext } from '../common/factories/makeExpandableSectionContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of ExpandableSectionWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type ExpandableSectionContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in an ExpandableSectionContext.
 */
export const ExpandableSectionContextWrapper = ({ children, id }: ExpandableSectionContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeExpandableSectionContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
