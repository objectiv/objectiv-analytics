/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackVisibilityOptions } from '../../definitions/TrackVisibilityOptions';
import { isTrackVisibilityAttribute } from '../guards/isTrackVisibilityAttribute';
import { parseJson } from './parseJson';

/**
 * `trackVisibility` Tagging Attribute parser
 */
export const parseTrackVisibility = (stringifiedTrackVisibilityAttribute: string | null): TrackVisibilityOptions => {
  const trackVisibilityAttribute = parseJson(stringifiedTrackVisibilityAttribute);

  if (!isTrackVisibilityAttribute(trackVisibilityAttribute)) {
    throw new Error(`trackVisibility attribute is not valid: ${JSON.stringify(stringifiedTrackVisibilityAttribute)}`);
  }

  if (trackVisibilityAttribute === true) {
    return { mode: 'auto' };
  }

  if (trackVisibilityAttribute === false) {
    return undefined;
  }

  return trackVisibilityAttribute;
};
