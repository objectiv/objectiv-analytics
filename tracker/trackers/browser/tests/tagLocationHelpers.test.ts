/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  LocationContextName,
  tagContent,
  tagExpandable,
  TaggingAttribute,
  tagInput,
  tagLink,
  tagMediaPlayer,
  tagNavigation,
  tagOverlay,
  tagPressable,
  tagRootLocation,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('tagLocationHelpers', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(tagContent()).toBeUndefined();
    // @ts-ignore
    expect(tagExpandable()).toBeUndefined();
    // @ts-ignore
    expect(tagInput()).toBeUndefined();
    // @ts-ignore
    expect(tagLink()).toBeUndefined();
    // @ts-ignore
    expect(tagMediaPlayer()).toBeUndefined();
    // @ts-ignore
    expect(tagNavigation()).toBeUndefined();
    // @ts-ignore
    expect(tagOverlay()).toBeUndefined();
    // @ts-ignore
    expect(tagRootLocation()).toBeUndefined();
    // @ts-ignore
    expect(tagPressable()).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ wrong: 'test-button' })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: undefined })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: 0 })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: false })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: true })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: {} })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: Infinity })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: -Infinity })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: 'test', options: 'nope' })).toBeUndefined();
    // @ts-ignore
    expect(tagPressable({ id: 'test', options: 'nope' }, null)).toBeUndefined();
  });

  it('tagPressable', () => {
    const taggingAttributes = tagPressable({ id: 'test-button' });

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

  it('tagContent', () => {
    const taggingAttributes = tagContent({ id: 'test-section' });

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

  it('tagExpandable', () => {
    const taggingAttributes = tagExpandable({ id: 'test-expandable' });

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

  it('tagInput', () => {
    const taggingAttributes = tagInput({ id: 'test-input' });

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

  it('tagInput with value tracking', () => {
    const taggingAttributes = tagInput({ id: 'test-input', options: { trackBlurs: { trackValue: true } } });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.InputContext,
        id: 'test-input',
      }),
      [TaggingAttribute.trackBlurs]: '{"trackValue":true}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('tagLink', () => {
    const taggingAttributes = tagLink({ id: 'link', href: '/test' });

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

  it('tagMediaPlayer', () => {
    const taggingAttributes = tagMediaPlayer({ id: 'test-media-player' });

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

  it('tagNavigation', () => {
    const taggingAttributes = tagNavigation({ id: 'test-nav' });

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

  it('tagOverlay', () => {
    const taggingAttributes = tagOverlay({ id: 'test-overlay' });

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

  it('tagRootLocation', () => {
    const taggingAttributes = tagRootLocation({ id: 'test-page' });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchUUID,
      [TaggingAttribute.context]: JSON.stringify({
        __instance_id: taggingAttributes ? JSON.parse(taggingAttributes[TaggingAttribute.context]).__instance_id : null,
        __location_context: true,
        _type: LocationContextName.RootLocationContext,
        id: 'test-page',
      }),
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });
});
