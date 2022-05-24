/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeContentContext } from '@objectiv/tracker-core';
import React from 'react';
import { LocationContextWrapper, LocationContextWrapperProps } from './LocationContextWrapper';

/**
 * The props of ContentContextWrapper.
 */
export type ContentContextWrapperProps = Pick<LocationContextWrapperProps, 'children'> & {
  /**
   * All ContentContexts must have an identifier. This should be something readable representing the section in the UI.
   * Sibling Components cannot have the same identifier.
   */
  id: string;
};

/**
 * Wraps its children in a ContentContext.
 */
export const ContentContextWrapper = ({ children, id }: ContentContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeContentContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
