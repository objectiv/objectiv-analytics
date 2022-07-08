/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackBlursAttribute } from '../../definitions/TrackBlursAttribute';
import { stringifyJson } from './stringifyJson';

/**
 * `trackBlurs` Tagging Attribute stringifier
 */
export const stringifyTrackBlurs = (trackBlursAttribute: TrackBlursAttribute) => {
  return stringifyJson(trackBlursAttribute);
};
