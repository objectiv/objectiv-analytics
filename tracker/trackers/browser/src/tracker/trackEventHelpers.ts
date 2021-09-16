import {
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeInputChangeEvent,
  makeSectionHiddenEvent,
  makeSectionVisibleEvent,
  makeURLChangeEvent,
  makeVideoPauseEvent,
  makeVideoStartEvent,
} from '@objectiv/tracker-core';
import { trackEvent } from '../tracker/trackEvent';
import { BrowserTracker } from './BrowserTracker';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

/**
 * The parameters of the Event helper functions
 */
export type TrackEventHelperParameters = {
  element: HTMLElement | EventTarget;
  tracker?: BrowserTracker;
};

/**
 * Event specific helpers. To make it easier to track common Events
 */
export const trackClick = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeClickEvent, element, tracker });
};

export const trackInputChange = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeInputChangeEvent, element, tracker });
};

export const trackSectionVisible = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeSectionVisibleEvent, element, tracker });
};

export const trackSectionHidden = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeSectionHiddenEvent, element, tracker });
};

export const trackVideoStart = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeVideoStartEvent, element, tracker });
};

export const trackVideoPause = ({ element, tracker }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeVideoPauseEvent, element, tracker });
};

export const trackVisibility = ({
  element,
  tracker,
  isVisible,
}: TrackEventHelperParameters & { isVisible: boolean }) => {
  return trackEvent({ eventFactory: isVisible ? makeSectionVisibleEvent : makeSectionHiddenEvent, element, tracker });
};

/**
 * The parameters of the Application Loaded and URLChange Event helper functions
 */
export type NonInteractiveTrackHelperParameters = {
  element?: HTMLElement | EventTarget;
  tracker?: BrowserTracker;
  onError?: TrackOnErrorCallback;
};

export const trackApplicationLoaded = (parameters: NonInteractiveTrackHelperParameters = {}) => {
  try {
    const { element = document, tracker } = parameters;
    return trackEvent({ eventFactory: makeApplicationLoadedEvent, element, tracker });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};

export const trackURLChange = (parameters: NonInteractiveTrackHelperParameters = {}) => {
  try {
    const { element = document, tracker } = parameters;
    return trackEvent({ eventFactory: makeURLChangeEvent, element, tracker });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
