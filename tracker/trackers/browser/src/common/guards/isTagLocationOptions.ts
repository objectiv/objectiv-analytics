/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TagLocationOptions } from '../../definitions/TagLocationOptions';
import { isTrackBlursAttribute } from './isTrackBlursAttribute';
import { isTrackClicksAttribute } from './isTrackClicksAttribute';
import { isTrackVisibilityAttribute } from './isTrackVisibilityAttribute';
import { isValidateAttribute } from './isValidateAttribute';

/**
 * A type guard to determine if the given object is a TagLocationOptions.
 */
export const isTagLocationOptions = (object: Partial<TagLocationOptions>): object is TagLocationOptions => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (object.trackClicks !== undefined && !isTrackClicksAttribute(object.trackClicks)) {
    return false;
  }

  if (object.trackBlurs !== undefined && !isTrackBlursAttribute(object.trackBlurs)) {
    return false;
  }

  if (object.trackVisibility !== undefined && !isTrackVisibilityAttribute(object.trackVisibility)) {
    return false;
  }

  // TODO parent

  if (object.validate !== undefined && !isValidateAttribute(object.validate)) {
    return false;
  }

  return true;
};
