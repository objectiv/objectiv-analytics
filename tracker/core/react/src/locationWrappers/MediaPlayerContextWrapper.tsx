/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeMediaPlayerContext } from '../common/factories/makeMediaPlayerContext';
import { LocationContextWrapper } from './LocationContextWrapper';

import { SectionContextWrapperProps } from './SectionContextWrapper';
/**
 * The props of MediaPlayerContextWrapper. No extra attributes, same as SectionContextWrapper.
 */
export type MediaPlayerContextWrapperProps = SectionContextWrapperProps;

/**
 * Wraps its children in a MediaPlayerContext.
 */
export const MediaPlayerContextWrapper = ({ children, id }: MediaPlayerContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeMediaPlayerContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
