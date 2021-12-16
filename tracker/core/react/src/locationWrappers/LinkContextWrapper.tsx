/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeLinkContext } from '../common/factories/makeLinkContext';
import { LocationContextWrapper } from './LocationContextWrapper';
import { SectionContextWrapperProps } from './SectionContextWrapper';

/**
 * The props of LinkContextWrapper.
 */
export type LinkContextWrapperProps = SectionContextWrapperProps & {
  /**
   * The text / label / title of the Link or a description of what it is about.
   */
  text: string;

  /**
   * Where is the link leading to. Eg: the href attribute of a <a> tag or the `to` prop of a Link component.
   */
  href: string;
};

/**
 * Wraps its children in a LinkContext.
 */
export const LinkContextWrapper = ({ children, id, text, href }: LinkContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeLinkContext({ id, text, href })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
