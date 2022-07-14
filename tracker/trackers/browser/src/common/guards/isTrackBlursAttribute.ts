/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackBlursAttribute } from '../../definitions/TrackBlursAttribute';

/**
 * A type guard to determine if the given object is TrackBlursAttribute.
 */
export const isTrackBlursAttribute = (attribute: Partial<TrackBlursAttribute>): attribute is TrackBlursAttribute => {
  if (typeof attribute !== 'boolean' && typeof attribute !== 'object') {
    return false;
  }

  if (attribute === null) {
    return false;
  }

  return !(typeof attribute === 'object' && typeof attribute.trackValue !== 'boolean');
};
