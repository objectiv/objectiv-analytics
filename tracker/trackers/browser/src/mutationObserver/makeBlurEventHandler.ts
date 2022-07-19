/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GlobalContexts, makeInputValueContext } from '@objectiv/tracker-core';
import { BrowserTracker } from '../BrowserTracker';
import { isTaggedElement } from '../common/guards/isTaggedElement';
import { TaggedElement } from '../definitions/TaggedElement';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { TrackBlursOptions } from '../definitions/TrackBlursOptions';
import { trackInputChangeEvent } from '../eventTrackers/trackInputChangeEvent';

/**
 * A factory to make the event handler to attach to new TaggedElements with the `trackBlurs` attributes set
 */
export const makeBlurEventHandler =
  (element: TaggedElement, tracker?: BrowserTracker, trackBlursOptions?: TrackBlursOptions, locationId?: string) =>
  (event: Event) => {
    if (
      // Either the Event's target is the TaggedElement itself
      event.target === element ||
      // Or the Event's currentTarget is am Element tagged to track Clicks (eg: the Event bubbled up to from a child)
      (isTaggedElement(event.currentTarget) && event.currentTarget.hasAttribute(TaggingAttribute.trackBlurs))
    ) {
      const globalContexts: GlobalContexts = [];

      if (
        trackBlursOptions?.trackValue &&
        locationId &&
        (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement)
      ) {
        globalContexts.push(
          makeInputValueContext({
            id: locationId,
            value: event.target.value,
          })
        );
      }

      trackInputChangeEvent({ element, tracker, globalContexts });
    }
  };
