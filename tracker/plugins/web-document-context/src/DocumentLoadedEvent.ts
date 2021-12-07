/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeDocumentLoadedEvent, Tracker } from '@objectiv/tracker-core';

/**
 * DocumentLoadedEvent is triggered by DOMContentLoaded. The actual URL can be retrieved from the WebDocumentContext
 */
export const trackDocumentLoadedEvent = (tracker: Tracker): void => {
  const trackEvent = () => tracker.trackEvent(makeDocumentLoadedEvent());

  if (document.readyState !== 'complete') {
    document.addEventListener('DOMContentLoaded', trackEvent);
  } else {
    trackEvent();
  }
};
