import { makeClickEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker } from '../src/';
import makeClickEventListener from '../src/observer/makeClickEventListener';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('makeClickEventListener', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should track Button Click when invoked from a valid target', () => {
    const trackedButton = makeTrackedElement('button', null, 'button');
    const clickEventListener = makeClickEventListener(trackedButton, window.objectiv.tracker);

    trackedButton.addEventListener('click', clickEventListener);
    trackedButton.dispatchEvent(new MouseEvent('click'));

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(1, makeClickEvent());
  });

  it('should not track Div Click when invoked from a bubbling target', () => {
    const trackedButton = makeTrackedElement('button', null, 'button');
    const trackedDiv = makeTrackedElement('div', null, 'div');
    const divClickEventListener = jest.fn(makeClickEventListener(trackedDiv, window.objectiv.tracker));

    trackedDiv.addEventListener('click', divClickEventListener);
    trackedButton.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(divClickEventListener).not.toHaveBeenCalled();
    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });
});
