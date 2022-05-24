/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makePressableContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of PressableContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type PressableContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in a PressableContext.
 */
export const PressableContextWrapper = ({ children, id }: PressableContextWrapperProps) => (
  <LocationContextWrapper locationContext={makePressableContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
