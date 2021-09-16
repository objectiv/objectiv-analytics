import {
  trackButton,
  trackElement,
  trackExpandableElement,
  TrackingAttribute,
  trackInput,
  trackLink,
  trackMediaPlayer,
  trackNavigation,
  trackOverlay,
} from '../src';
import matchElementId from './mocks/matchElementId';

describe('trackLocationHelpers', () => {
  it('should return an empty object when error occurs', () => {
    // @ts-ignore
    expect(trackElement()).toBeUndefined();
    // @ts-ignore
    expect(trackExpandableElement()).toBeUndefined();
    // @ts-ignore
    expect(trackInput()).toBeUndefined();
    // @ts-ignore
    expect(trackLink()).toBeUndefined();
    // @ts-ignore
    expect(trackMediaPlayer()).toBeUndefined();
    // @ts-ignore
    expect(trackNavigation()).toBeUndefined();
    // @ts-ignore
    expect(trackOverlay()).toBeUndefined();
    // @ts-ignore
    expect(trackButton()).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ wrong: 'test-button' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: undefined })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: 0, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: false, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: true, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: {}, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: Infinity, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: -Infinity, text: 'test' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: 'test', text: 'test', options: 'nope' })).toBeUndefined();
    // @ts-ignore
    expect(trackButton({ id: 'test', text: 'test', options: 'nope' }, null)).toBeUndefined();
  });

  it('trackButton', () => {
    const trackingAttributes = trackButton({ id: 'test-button', text: 'Click Me' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        __action_context: true,
        _type: 'ButtonContext',
        id: 'test-button',
        text: 'Click Me',
      }),
      [TrackingAttribute.trackClicks]: 'true',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackElement', () => {
    const trackingAttributes = trackElement({ id: 'test-section' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'SectionContext',
        id: 'test-section',
      }),
      [TrackingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackExpandableElement', () => {
    const trackingAttributes = trackExpandableElement({ id: 'test-expandable' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'ExpandableSectionContext',
        id: 'test-expandable',
      }),
      [TrackingAttribute.trackClicks]: 'true',
      [TrackingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackInput', () => {
    const trackingAttributes = trackInput({ id: 'test-input' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        _type: 'InputContext',
        id: 'test-input',
      }),
      [TrackingAttribute.trackBlurs]: 'true',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackLink', () => {
    const trackingAttributes = trackLink({ id: 'link', text: 'Click Me', href: '/test' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __item_context: true,
        __action_context: true,
        _type: 'LinkContext',
        id: 'link',
        text: 'Click Me',
        href: '/test',
      }),
      [TrackingAttribute.trackClicks]: 'true',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackMediaPlayer', () => {
    const trackingAttributes = trackMediaPlayer({ id: 'test-media-player' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'MediaPlayerContext',
        id: 'test-media-player',
      }),
      [TrackingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackNavigation', () => {
    const trackingAttributes = trackNavigation({ id: 'test-nav' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'NavigationContext',
        id: 'test-nav',
      }),
      [TrackingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });

  it('trackOverlay', () => {
    const trackingAttributes = trackOverlay({ id: 'test-overlay' });

    const expectedTrackingAttributes = {
      [TrackingAttribute.elementId]: matchElementId,
      [TrackingAttribute.context]: JSON.stringify({
        __location_context: true,
        __section_context: true,
        _type: 'OverlayContext',
        id: 'test-overlay',
      }),
      [TrackingAttribute.trackVisibility]: '{"mode":"auto"}',
    };

    expect(trackingAttributes).toStrictEqual(expectedTrackingAttributes);
  });
});
