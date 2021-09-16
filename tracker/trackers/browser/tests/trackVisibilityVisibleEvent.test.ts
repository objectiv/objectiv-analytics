import { makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, TrackingAttribute } from '../src';
import trackVisibilityVisibleEvent from '../src/observer/trackVisibilityVisibleEvent';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('trackVisibilityVisibleEvent', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should not track elements without visibility tracking attributes', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tracking attributes', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, 'null');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:auto', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeSectionVisibleEvent());
  });

  it('should not track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTrackedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityVisibleEvent(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });
});
