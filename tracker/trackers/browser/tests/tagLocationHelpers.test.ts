import {
  tagButton,
  tagElement,
  tagExpandableElement,
  TaggingAttribute,
  tagInput,
  tagLink,
  tagMediaPlayer,
  tagNavigation,
  tagOverlay,
} from '../src';
import { matchElementId } from './mocks/matchElementId';

describe('tagLocationHelpers', () => {
  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(tagElement()).toBeUndefined();
    // @ts-ignore
    expect(tagExpandableElement()).toBeUndefined();
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
    expect(tagButton()).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ wrong: 'test-button' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: undefined })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: 0, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: false, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: true, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: {}, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: Infinity, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: -Infinity, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: 'test', text: 'test', options: 'nope' })).toBeUndefined();
    // @ts-ignore
    expect(tagButton({ id: 'test', text: 'test', options: 'nope' }, null)).toBeUndefined();
  });

  it('tagButton', () => {
    const taggingAttributes = tagButton({ id: 'test-button', text: 'Click Me' });

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

  it('tagElement', () => {
    const taggingAttributes = tagElement({ id: 'test-section' });

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

  it('tagExpandableElement', () => {
    const taggingAttributes = tagExpandableElement({ id: 'test-expandable' });

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

  it('tagInput', () => {
    const taggingAttributes = tagInput({ id: 'test-input' });

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

  it('tagLink', () => {
    const taggingAttributes = tagLink({ id: 'link', text: 'Click Me', href: '/test' });

    const expectedTaggingAttributes = {
      [TaggingAttribute.elementId]: matchElementId,
      [TaggingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        __action_context: true,
        _type: 'LinkContext',
        id: 'link',
        text: 'Click Me',
        href: '/test',
      }),
      [TaggingAttribute.trackClicks]: 'true',
    };

    expect(taggingAttributes).toStrictEqual(expectedTaggingAttributes);
  });

  it('tagMediaPlayer', () => {
    const taggingAttributes = tagMediaPlayer({ id: 'test-media-player' });

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

  it('tagNavigation', () => {
    const taggingAttributes = tagNavigation({ id: 'test-nav' });

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

  it('tagOverlay', () => {
    const taggingAttributes = tagOverlay({ id: 'test-overlay' });

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
});
