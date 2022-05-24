/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeRootLocationContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of RootLocationContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type RootLocationContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in an RootLocationContext.
 */
export const RootLocationContextWrapper = ({ children, id }: RootLocationContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeRootLocationContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
