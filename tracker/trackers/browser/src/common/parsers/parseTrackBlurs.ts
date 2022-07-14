/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackBlursOptions } from '../../definitions/TrackBlursOptions';
import { isTrackBlursAttribute } from '../guards/isTrackBlursAttribute';
import { parseJson } from './parseJson';

/**
 * `trackBlurs` Tagging Attribute to TrackBlursOptions parser
 */
export const parseTrackBlurs = (stringifiedTrackBlursAttribute: string | null): TrackBlursOptions => {
  const parsedTrackBlurs = parseJson(stringifiedTrackBlursAttribute);

  if (!isTrackBlursAttribute(parsedTrackBlurs)) {
    throw new Error(`Invalid trackClicks attribute: ${JSON.stringify(stringifiedTrackBlursAttribute)}`);
  }

  if (parsedTrackBlurs === true) {
    return {
      trackValue: false,
    };
  } else if (parsedTrackBlurs === false) {
    return undefined;
  }

  return parsedTrackBlurs;
};
