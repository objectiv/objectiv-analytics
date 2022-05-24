/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeExpandableContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of ExpandableContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type ExpandableContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in an ExpandableContext.
 */
export const ExpandableContextWrapper = ({ children, id }: ExpandableContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeExpandableContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
