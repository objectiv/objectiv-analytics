/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  LocationContextName,
  makeContentContext,
  makeExpandableContext,
  makeInputContext,
  makeLinkContext,
  makeMediaPlayerContext,
  makeNavigationContext,
  makeOverlayContext,
  makePressableContext,
} from '@objectiv/tracker-core';
import { tagContent, TaggingAttribute, tagLocation, tagOverlay } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('tagLocation', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(tagLocation()).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({})).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: null })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: undefined })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: 0 })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: false })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: true })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: {} })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: Infinity })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: -Infinity })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: { _type: 'nope' } })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: { _type: LocationContextName.ContentContext } })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: { id: 'nope' } })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: { _type: 'Nope', id: 'nope' } })).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: makeContentContext({ id: 'test' }), options: 'invalid' })).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackClicks: null } })
    ).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackClicks: 'nope' } })
    ).toBeUndefined();
    // @ts-ignore
    expect(tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackClicks: {} } })).toBeUndefined();
    expect(
      tagLocation({
        instance: makeContentContext({ id: 'test' }),
        // @ts-ignore
        options: { trackClicks: { waitUntilTracked: 'nope' } },
      })
    ).toBeUndefined();
    // @ts-ignore
    expect(
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackClicks: { waitUntilTracked: {} } } })
    ).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackBlurs: 'nope' } })
    ).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackVisibility: 'nope' } })
    ).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { trackVisibility: {} } })
    ).toBeUndefined();
    expect(
      // @ts-ignore
      tagLocation({ instance: makeContentContext({ id: 'test' }), options: { validate: 'nope' } })
    ).toBeUndefined();
  });

  it('should call `onError` callback when an error occurs', () => {
    const errorCallback = jest.fn();

    // @ts-ignore
    tagLocation({ instance: {}, onError: errorCallback });

    expect(errorCallback).toHaveBeenCalledTimes(1);
    expect(errorCallback.mock.calls[0][0]).toBeInstanceOf(Error);
  });

  it('should call `TrackerConsole.error` when an error occurs and `onError` has not been provided', () => {
    // @ts-ignore
    tagLocation({ instance: {} });

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  it('should allow overriding whether to track click, blur and visibility events via options', () => {
    const taggingAttributesA = tagContent({ id: 'test' });
    expect(taggingAttributesA).toStrictEqual({
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributesA
          ? JSON.parse(taggingAttributesA[TaggingAttribute.context]).__instance_id
          : null,
        __location_context: true,
        _type: LocationContextName.ContentContext,
        id: 'test',
      }),
    });

    const taggingAttributesB = tagOverlay({
      id: 'test',
      options: {
        trackVisibility: false,
      },
    });
    expect(taggingAttributesB).toStrictEqual({
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributesB
          ? JSON.parse(taggingAttributesB[TaggingAttribute.context]).__instance_id
          : null,
        __location_context: true,
        _type: LocationContextName.OverlayContext,
        id: 'test',
      }),
    });

    const taggingAttributesC = tagContent({
      id: 'test',
      options: {
        trackClicks: false,
        trackBlurs: true,
        trackVisibility: { mode: 'manual', isVisible: true },
      },
    });
    expect(taggingAttributesC).toStrictEqual({
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributesC
          ? JSON.parse(taggingAttributesC[TaggingAttribute.context]).__instance_id
          : null,
        __location_context: true,
        _type: LocationContextName.ContentContext,
        id: 'test',
      }),
      [TaggingAttribute.trackClicks]: 'false',
      [TaggingAttribute.trackBlurs]: 'true',
      [TaggingAttribute.trackVisibility]: '{"mode":"manual","isVisible":true}',
    });
  });

  it('should allow overriding parent auto detection via options', () => {
    const parent = tagContent({ id: 'parent' });
    const taggingAttributesA = tagContent({ id: 'test' });
    expect(taggingAttributesA).toStrictEqual({
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributesA
          ? JSON.parse(taggingAttributesA[TaggingAttribute.context]).__instance_id
          : null,
        __location_context: true,
        _type: LocationContextName.ContentContext,
        id: 'test',
      }),
    });
    const taggingAttributesB = tagContent({ id: 'test', options: { parent } });
    expect(taggingAttributesB).toStrictEqual({
      [TaggingAttribute.elementId]: matchUUID,
      // @ts-ignore
      [TaggingAttribute.parentElementId]: parent[TaggingAttribute.elementId],
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributesB
          ? JSON.parse(taggingAttributesB[TaggingAttribute.context]).__instance_id
          : null,
        __location_context: true,
        _type: LocationContextName.ContentContext,
        id: 'test',
      }),
    });
  });

  it('should return Pressable tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makePressableContext({ id: 'test-button' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        __pressable_context: true,
        _type: LocationContextName.PressableContext,
        id: 'test-button',
      }),
      [TaggingAttribute.trackClicks]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Content tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeContentContext({ id: 'test-section' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.ContentContext,
        id: 'test-section',
      }),
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return ExpandableElement (Expandable) tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makeExpandableContext({ id: 'test-expandable' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.ExpandableContext,
        id: 'test-expandable',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Input tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeInputContext({ id: 'test-input' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.InputContext,
        id: 'test-input',
      }),
      [TaggingAttribute.trackBlurs]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Link tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makeLinkContext({ id: 'link', href: '/test' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        __pressable_context: true,
        _type: LocationContextName.LinkContext,
        id: 'link',
        href: '/test',
      }),
      [TaggingAttribute.trackClicks]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return MediaPlayer tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeMediaPlayerContext({ id: 'test-media-player' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.MediaPlayerContext,
        id: 'test-media-player',
      }),
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Navigation tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeNavigationContext({ id: 'test-nav' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.NavigationContext,
        id: 'test-nav',
      }),
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Overlay tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeOverlayContext({ id: 'test-overlay' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.OverlayContext,
        id: 'test-overlay',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });
});
