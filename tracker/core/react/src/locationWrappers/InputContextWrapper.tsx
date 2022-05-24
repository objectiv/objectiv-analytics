/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeInputContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of InputContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type InputContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in a InputContext.
 */
export const InputContextWrapper = ({ children, id }: InputContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeInputContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
