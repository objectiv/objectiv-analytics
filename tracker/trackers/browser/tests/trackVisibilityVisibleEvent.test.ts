import { generateUUID, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, makeTracker, TaggingAttribute } from '../src';
import { trackVisibilityVisibleEvent } from '../src/observer/trackVisibilityVisibleEvent';
import { makeTaggedElement } from './mocks/makeTaggedElement';

describe('trackVisibilityVisibleEvent', () => {
  beforeAll(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should not track elements without visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, 'null');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:auto', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should not track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });
});
