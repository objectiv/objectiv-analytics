/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionContext } from '../common/factories/makeSectionContext';
import { LocationContextWrapper, LocationContextWrapperProps } from './LocationContextWrapper';

/**
 * The props of SectionContextWrapper.
 */
export type SectionContextWrapperProps = Pick<LocationContextWrapperProps, 'children'> & {
  /**
   * All SectionContexts must have an identifier. This should be something readable representing the section in the UI.
   * Sibling Components cannot have the same identifier.
   */
  id: string;
};

/**
 * Wraps its children in a SectionContext.
 */
export const SectionContextWrapper = ({ children, id }: SectionContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeSectionContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
