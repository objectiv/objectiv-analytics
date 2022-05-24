/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeNavigationContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of NavigationContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type NavigationContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in a NavigationContext.
 */
export const NavigationContextWrapper = ({ children, id }: NavigationContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeNavigationContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
