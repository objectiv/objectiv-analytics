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
import { tagLocation, TagLocationOptions, TagLocationParameters, TagLocationReturnValue } from '../tracker/tagLocation';
import { trackerErrorHandler, TrackOnErrorCallback } from '../trackerErrorHandler';

/**
 * Tag Location helpers automatically factor Context Instances and use `tagLocation` internally.
 */
export const TagLocationHelperParameters = assign(
  pick(TagLocationParameters, ['options', 'onError']),
  object({
    id: string(),
  })
);
export type TagLocationHelperParameters = {
  id: string;
  options?: TagLocationOptions;
  onError?: TrackOnErrorCallback;
};

/**
 * tagElement helper
 */
export const tagElement = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeSectionContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagExpandableElement helper
 */
export const tagExpandableElement = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeExpandableSectionContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagInput helper
 */
export const tagInput = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeInputContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagButton helper
 */
export const TagButtonParameters = assign(TagLocationHelperParameters, object({ text: string() }));
export type TagButtonParameters = TagLocationHelperParameters & { text: string };
export const tagButton = (parameters: TagButtonParameters): TagLocationReturnValue => {
  try {
    const { id, text, options } = create(parameters, TagButtonParameters);
    return tagLocation({ instance: makeButtonContext({ id, text }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagLink helper
 */
export const TagLinkParameters = assign(TagLocationHelperParameters, object({ text: string(), href: string() }));
export type TagLinkParameters = TagLocationHelperParameters & { text: string; href: string };
export const tagLink = (parameters: TagLinkParameters): TagLocationReturnValue => {
  try {
    const { id, text, href, options } = create(parameters, TagLinkParameters);
    // TODO attempt auto-detecting if href is external and use that to set `waitUntilTracked` accordingly
    return tagLocation({ instance: makeLinkContext({ id, text, href }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagMediaPlayer helper
 */
export const tagMediaPlayer = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeMediaPlayerContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagNavigation helper
 */
export const tagNavigation = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeNavigationContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};

/**
 * tagOverlay helper
 */
export const tagOverlay = (parameters: TagLocationHelperParameters): TagLocationReturnValue => {
  try {
    const { id, options } = create(parameters, TagLocationHelperParameters);
    return tagLocation({ instance: makeOverlayContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
