import { makeSectionHiddenEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, TrackingAttribute } from '../src';
import trackVisibilityHiddenEvent from '../src/observer/trackVisibilityHiddenEvent';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('trackVisibilityHiddenEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should not track elements without visibility tracking attributes', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');

    trackVisibilityHiddenEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tracking attributes', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, 'null');

    trackVisibilityHiddenEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should not track in mode:auto', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityHiddenEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should not track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityHiddenEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityHiddenEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeSectionHiddenEvent());
  });

  it('should use given tracker instead of the global one', async () => {
    const trackerOverride = new BrowserTracker({ applicationId: 'override', endpoint: 'override' });
    jest.spyOn(trackerOverride, 'trackEvent');

    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityHiddenEvent(trackedDiv, trackerOverride);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).toHaveBeenCalledTimes(1);
    expect(trackerOverride.trackEvent).toHaveBeenNthCalledWith(1, makeSectionHiddenEvent());
  });
});
