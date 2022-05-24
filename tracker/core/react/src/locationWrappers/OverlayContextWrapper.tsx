/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeOverlayContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of OverlayContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type OverlayContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in an OverlayContext.
 */
export const OverlayContextWrapper = ({ children, id }: OverlayContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeOverlayContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
