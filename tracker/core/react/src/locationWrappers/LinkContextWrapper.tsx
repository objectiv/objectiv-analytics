/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeLinkContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * The props of LinkContextWrapper.
 */
export type LinkContextWrapperProps = ContentContextWrapperProps & {
  /**
   * Where is the link leading to. Eg: the href attribute of a <a> tag or the `to` prop of a Link component.
   */
  href: string;
};

/**
 * Wraps its children in a LinkContext.
 */
export const LinkContextWrapper = ({ children, id, href }: LinkContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeLinkContext({ id, href })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
