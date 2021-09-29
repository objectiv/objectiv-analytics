import { makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, TaggingAttribute } from '../src';
import { trackVisibilityVisibleEvent } from '../src/observer/trackVisibilityVisibleEvent';
import { makeTaggedElement } from './mocks/makeTaggedElement';

describe('trackVisibilityVisibleEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should not track elements without visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, 'null');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:auto', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should not track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });
});
