/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeOverlayContext } from '@objectiv/tracker-core';
import { create } from 'superstruct';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { LocationTaggerParameters } from '../definitions/LocationTaggerParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagOverlay is a shorthand for tagLocation. It eases the tagging of OverlayContext bound Elements
 */
export const tagOverlay = (parameters: LocationTaggerParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, LocationTaggerParameters);
    return tagLocation({ instance: makeOverlayContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
