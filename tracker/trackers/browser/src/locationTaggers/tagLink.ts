/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeLinkContext } from '@objectiv/tracker-core';
import { create } from 'superstruct';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TagLinkParameters } from '../definitions/TagLinkParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagLink is a shorthand for tagLocation. It eases the tagging of LinkContext bound Elements
 */
export const tagLink = (parameters: TagLinkParameters): TagLocationReturnValue => {
  try {
    const { id, text, href, options } = create(parameters, TagLinkParameters);
    return tagLocation({ instance: makeLinkContext({ id, text, href }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
