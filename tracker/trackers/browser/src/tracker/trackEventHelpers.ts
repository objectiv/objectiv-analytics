import {
  makeAbortedEvent,
  makeApplicationLoadedEvent,
  makeClickEvent,
  makeCompletedEvent,
  makeInputChangeEvent,
  makeSectionHiddenEvent,
  makeSectionVisibleEvent,
  makeURLChangeEvent,
  makeVideoPauseEvent,
  makeVideoStartEvent,
} from '@objectiv/tracker-core';
import { trackEvent } from '../tracker/trackEvent';
import { TaggableElement } from '../typeGuards';
import { BrowserTracker } from './BrowserTracker';
import { trackerErrorHandler, TrackOnErrorCallback } from '../trackerErrorHandler';

/**
 * The parameters of the Event helper functions
 */
export type TrackEventHelperParameters = {
  element: TaggableElement | EventTarget;
  tracker?: BrowserTracker;
  onError?: TrackOnErrorCallback;
};

/**
 * Event specific helpers. To make it easier to track common Events
 */
export const trackClick = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeClickEvent, element, tracker, onError });
};

export const trackInputChange = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeInputChangeEvent, element, tracker, onError });
};

export const trackSectionVisible = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeSectionVisibleEvent, element, tracker, onError });
};

export const trackSectionHidden = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeSectionHiddenEvent, element, tracker, onError });
};

export const trackVideoStart = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeVideoStartEvent, element, tracker, onError });
};

export const trackVideoPause = ({ element, tracker, onError }: TrackEventHelperParameters) => {
  return trackEvent({ eventFactory: makeVideoPauseEvent, element, tracker, onError });
};

export const trackVisibility = ({
  element,
  tracker,
  isVisible,
  onError,
}: TrackEventHelperParameters & { isVisible: boolean }) => {
  return trackEvent({
    eventFactory: isVisible ? makeSectionVisibleEvent : makeSectionHiddenEvent,
    element,
    tracker,
    onError,
  });
};

/**
 * The parameters of the Application Loaded and URLChange Event helper functions
 */
export type NonInteractiveTrackHelperParameters = {
  element?: TaggableElement | EventTarget;
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

export const trackCompleted = (parameters: NonInteractiveTrackHelperParameters = {}) => {
  try {
    const { element = document, tracker } = parameters;
    return trackEvent({ eventFactory: makeCompletedEvent, element, tracker });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};

export const trackAborted = (parameters: NonInteractiveTrackHelperParameters = {}) => {
  try {
    const { element = document, tracker } = parameters;
    return trackEvent({ eventFactory: makeAbortedEvent, element, tracker });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
