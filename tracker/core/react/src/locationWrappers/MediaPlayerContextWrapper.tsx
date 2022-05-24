/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaPlayerContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of MediaPlayerContextWrapper. No extra attributes, same as ContentContextWrapper.
 */
export type MediaPlayerContextWrapperProps = ContentContextWrapperProps;

/**
 * Wraps its children in a MediaPlayerContext.
 */
export const MediaPlayerContextWrapper = ({ children, id }: MediaPlayerContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeMediaPlayerContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
