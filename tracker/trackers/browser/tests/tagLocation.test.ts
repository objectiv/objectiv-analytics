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
import { StructError } from 'superstruct';
import { tagElement, TaggingAttribute, tagLocation } from '../src';
import { matchElementId } from './mocks/matchElementId';

describe('tagLocation', () => {
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
    expect(tagLocation({ instance: makeSectionContext({ id: 'test' }), options: 'invalid' })).toBeUndefined();
  });

  it('should call `onError` callback when an error occurs', () => {
    const errorCallback = jest.fn();

    // @ts-ignore
    tagLocation({ instance: {}, onError: errorCallback });

    expect(errorCallback).toHaveBeenCalledTimes(1);
    expect(errorCallback.mock.calls[0][0]).toBeInstanceOf(StructError);
  });

  it('should call `console.error` when an error occurs and `onError` has not been provided', () => {
    const consoleErrorMock = jest.spyOn(console, 'error');

    // @ts-ignore
    tagLocation({ instance: {} });

    expect(consoleErrorMock).toHaveBeenCalledTimes(1);
  });

  it('should allow overriding whether to track click, blur and visibility events via options', () => {
    expect(tagElement({ id: 'test' })).toStrictEqual({
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    });
    expect(
      tagElement({
        id: 'test',
        options: {
          trackClicks: false,
          trackBlurs: true,
          trackVisibility: { mode: 'manual', isVisible: true },
        },
      })
    ).toStrictEqual({
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test',
      }),
      [TaggingAttribute.trackClicks]: 'false',
      [TaggingAttribute.trackBlurs]: 'true',
      [TaggingAttribute.trackVisibility]: '{"mode":"manual","isVisible":true}',
    });
  });

  it('should allow overriding parent auto detection via options', () => {
    const parent = tagElement({ id: 'parent' });
    expect(tagElement({ id: 'test' })).toStrictEqual({
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    });
    expect(tagElement({ id: 'test', options: { parent } })).toStrictEqual({
      [TaggingAttribute.elementId]: matchElementId,
      // @ts-ignore
      [TaggingAttribute.parentElementId]: parent[TaggingAttribute.elementId],
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    });
  });

  it('should return Button tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makeButtonContext({ id: 'test-button', text: 'Click Me' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        __action_context: true,
        _type: 'ButtonContext',
        id: 'test-button',
        text: 'Click Me',
      }),
      [TaggingAttribute.trackClicks]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Element (Section) tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeSectionContext({ id: 'test-section' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test-section',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return ExpandableElement (ExpandableSection) tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makeExpandableSectionContext({ id: 'test-expandable' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'ExpandableSectionContext',
        id: 'test-expandable',
      }),
      [TaggingAttribute.trackClicks]: 'true',
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Input tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeInputContext({ id: 'test-input' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        _type: 'InputContext',
        id: 'test-input',
      }),
      [TaggingAttribute.trackBlurs]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Link tagging attributes', () => {
    const taggingAttributes = tagLocation({
      instance: makeLinkContext({ id: 'link', text: 'link', href: '/test' }),
    });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        __action_context: true,
        _type: 'LinkContext',
        id: 'link',
        text: 'link',
        href: '/test',
      }),
      [TaggingAttribute.trackClicks]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return MediaPlayer tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeMediaPlayerContext({ id: 'test-media-player' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'MediaPlayerContext',
        id: 'test-media-player',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Navigation tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeNavigationContext({ id: 'test-nav' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'NavigationContext',
        id: 'test-nav',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should return Overlay tagging attributes', () => {
    const taggingAttributes = tagLocation({ instance: makeOverlayContext({ id: 'test-overlay' }) });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'OverlayContext',
        id: 'test-overlay',
      }),
      [TaggingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('should not allow extra attributes', () => {
    const customSectionContext = { ...makeSectionContext({ id: 'test-overlay' }), extraMetadata: { test: 123 } };
    const taggingAttributes = tagLocation({
      instance: customSectionContext,
      onError: (error) => console.log(error),
    });

    expect(taggingAttributes).toBeUndefined();
  });
});
