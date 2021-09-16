import {
  makeButtonContext,
  makeExpandableSectionContext,
  makeInputContext,
  makeLinkContext,
  makeMediaPlayerContext,
  makeNavigationContext,
  makeOverlayContext,
  makeSectionContext,
} from '@objectiv/tracker-core';
import { assign, create, object, pick, string } from 'superstruct';
import {
  trackLocation,
  TrackLocationOptions,
  TrackLocationParameters,
  TrackLocationReturnValue,
} from '../tracker/trackLocation';
import { trackerErrorHandler, TrackOnErrorCallback } from './trackerErrorHandler';

/**
 * Track Location helpers automatically factor Context Instances and use `track` internally.
 */
export const TrackLocationHelperParameters = assign(
  pick(TrackLocationParameters, ['options', 'onError']),
  object({
    id: string(),
  })
);
export type TrackLocationHelperParameters = {
  id: string;
  options?: TrackLocationOptions;
  onError?: TrackOnErrorCallback;
};

/**
 * TrackElement helper
 */
export const trackElement = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeSectionContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackExpandableElement helper
 */
export const trackExpandableElement = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeExpandableSectionContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackInput helper
 */
export const trackInput = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeInputContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackButton helper
 */
export const TrackButtonParameters = assign(TrackLocationHelperParameters, object({ text: string() }));
export type TrackButtonParameters = TrackLocationHelperParameters & { text: string };
export const trackButton = (parameters: TrackButtonParameters): TrackLocationReturnValue => {
  try {
    const { id, text, options } = create(parameters, TrackButtonParameters);
    return trackLocation({ instance: makeButtonContext({ id, text }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackLink helper
 */
export const TrackLinkParameters = assign(TrackLocationHelperParameters, object({ text: string(), href: string() }));
export type TrackLinkParameters = TrackLocationHelperParameters & { text: string; href: string };
export const trackLink = (parameters: TrackLinkParameters): TrackLocationReturnValue => {
  try {
    const { id, text, href, options } = create(parameters, TrackLinkParameters);
    return trackLocation({ instance: makeLinkContext({ id, text, href }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackMediaPlayer helper
 */
export const trackMediaPlayer = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeMediaPlayerContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackNavigation helper
 */
export const trackNavigation = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeNavigationContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * TrackOverlay helper
 */
export const trackOverlay = (parameters: TrackLocationHelperParameters): TrackLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TrackLocationHelperParameters);
    return trackLocation({ instance: makeOverlayContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
