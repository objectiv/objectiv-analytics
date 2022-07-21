/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { generateGUID, getObjectKeys, LocationContextName } from '@objectiv/tracker-core';
import { isPressableContext } from '../common/guards/isPressableContext';
import { isShowableContext } from '../common/guards/isShowableContext';
import { isTagLocationParameters } from '../common/guards/isTagLocationParameters';
import { runIfValueIsNotUndefined } from '../common/runIfValueIsNotUndefined';
import { stringifyLocationContext } from '../common/stringifiers/stringifyLocationContext';
import { stringifyTrackBlurs } from '../common/stringifiers/stringifyTrackBlurs';
import { stringifyTrackClicks } from '../common/stringifiers/stringifyTrackClicks';
import { stringifyTrackVisibility } from '../common/stringifiers/stringifyTrackVisibility';
import { stringifyValidate } from '../common/stringifiers/stringifyValidate';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { TagLocationParameters } from '../definitions/TagLocationParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';

/**
 * Used to decorate a Taggable Element with our Tagging Attributes.
 *
 * Returns an object containing the Tagging Attributes. It's properties are supposed to be spread on the target HTML
 * Element. This allows us to identify elements uniquely in a Document and to reconstruct their Location.
 *
 * For a higher level api see the tagLocationHelpers module.
 *
 * Examples
 *
 *    tagLocation({ instance: makeElementContext({ id: 'section-id' }) })
 *    tagLocation({ instance: makeElementContext({ id: 'section-id' }), { trackClicks: true } })
 *
 */
export const tagLocation = (parameters: TagLocationParameters): TagLocationReturnValue => {
  try {
    if (!isTagLocationParameters(parameters)) {
      throw new Error(`Invalid tagLocation parameters: ${JSON.stringify(parameters)}`);
    }

    const { instance, options } = parameters;

    // Determine Context type
    const isPressable = isPressableContext(instance);
    const isInput = instance._type === LocationContextName.InputContext;
    const isShowable = isShowableContext(instance);

    // Process options. Gather default attribute values
    const trackClicks = options?.trackClicks ?? (isPressable ? true : undefined);
    const trackBlurs = options?.trackBlurs ?? (isInput ? true : undefined);
    const parentElementId = options?.parent ? options.parent[TaggingAttribute.elementId] : undefined;

    // Determine whether to auto-track visibility
    let trackVisibility = options?.trackVisibility !== false ? options?.trackVisibility : undefined;
    if ((options?.trackVisibility === undefined && isShowable) || options?.trackVisibility === true) {
      trackVisibility = { mode: 'auto' };
    }

    // Create output attributes object
    const LocationTaggingAttributes = {
      [TaggingAttribute.elementId]: generateGUID(),
      [TaggingAttribute.parentElementId]: parentElementId,
      [TaggingAttribute.context]: stringifyLocationContext(instance),
      [TaggingAttribute.trackClicks]: runIfValueIsNotUndefined(stringifyTrackClicks, trackClicks),
      [TaggingAttribute.trackBlurs]: runIfValueIsNotUndefined(stringifyTrackBlurs, trackBlurs),
      [TaggingAttribute.trackVisibility]: runIfValueIsNotUndefined(stringifyTrackVisibility, trackVisibility),
      [TaggingAttribute.validate]: runIfValueIsNotUndefined(stringifyValidate, options?.validate),
    };

    // Strip out undefined attributes and return
    getObjectKeys(LocationTaggingAttributes).forEach((key) => {
      if (LocationTaggingAttributes[key] === undefined) {
        delete LocationTaggingAttributes[key];
      }
    });

    return LocationTaggingAttributes;
  } catch (error) {
    return trackerErrorHandler(error, parameters, parameters?.onError);
  }
};
