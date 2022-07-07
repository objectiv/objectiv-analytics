/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackClicksOptions } from '../../definitions/TrackClicksOptions';
import { isTrackClicksAttribute } from '../guards/isTrackClicksAttribute';
import { parseJson } from './parseJson';

/**
 * `trackClicks` Tagging Attribute to TrackClicksOptions parser
 * Differently than other simplistic parsers, this one transforms the `trackClicks` attribute in a different format.
 */
export const parseTrackClicks = (stringifiedTrackClicksAttribute: string | null): TrackClicksOptions => {
  const parsedTrackClicks = parseJson(stringifiedTrackClicksAttribute);

  if (!isTrackClicksAttribute(parsedTrackClicks)) {
    throw new Error(`Invalid trackClicks attribute: ${JSON.stringify(stringifiedTrackClicksAttribute)}`);
  }

  // Process `true` and `false` shorthands onto their verbose options counterparts
  if (typeof parsedTrackClicks == 'boolean') {
    return parsedTrackClicks ? {} : undefined;
  }

  // Else it must be already an object, from here on trackClicks.enabled will always be `true`
  let trackClickOptions: TrackClicksOptions = {};
  const { waitUntilTracked } = parsedTrackClicks;

  // Process `waitUntilTracked` shorthands - we only have a `true` shorthands to process, `false` means no option
  if (typeof waitUntilTracked == 'boolean') {
    // An empty object means `waitForQueue` will use default internal values for both `timeoutMs` and `intervalMs`
    trackClickOptions.waitForQueue = {};
    // The default `flushQueue` value is to always flush
    trackClickOptions.flushQueue = true;
  } else {
    // waitUntilTracked must be an object
    const { flushQueue, ...waitForQueue } = waitUntilTracked;
    trackClickOptions.flushQueue = flushQueue !== undefined ? flushQueue : true;
    trackClickOptions.waitForQueue = waitForQueue;
  }

  return trackClickOptions;
};
