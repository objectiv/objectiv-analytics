import {
  makeButtonContext,
  makeInputContext,
  makeSectionContext,
  makeSectionVisibleEvent,
} from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, TrackingAttribute } from '../src';
import trackNewElement from '../src/observer/trackNewElement';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('trackNewElement', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should skip the Element if it is not a Tracked Element', async () => {
    const div = document.createElement('div');
    jest.spyOn(div, 'addEventListener');

    trackNewElement(div, window.objectiv.tracker);

    expect(div.addEventListener).not.toHaveBeenCalled();
    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should track visibility: visible event', async () => {
    const sectionContext = makeSectionContext({ id: 'test' });
    const trackedDiv = makeTrackedElement('div-id-1', 'test', 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"auto"}');
    jest.spyOn(trackedDiv, 'addEventListener');

    trackNewElement(trackedDiv, window.objectiv.tracker);

    expect(trackedDiv.addEventListener).not.toHaveBeenCalled();
    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      makeSectionVisibleEvent({ location_stack: [sectionContext] })
    );
  });

  it('should attach click event listener', async () => {
    const buttonContext = makeButtonContext({ id: 'test', text: 'test' });
    const trackedButton = makeTrackedElement('button-id-1', JSON.stringify(buttonContext), 'button');
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TrackingAttribute.trackClicks, 'true');
    document.body.appendChild(trackedButton);
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, window.objectiv.tracker);

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function));
    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should attach blur event listener', async () => {
    const inputContext = makeInputContext({ id: 'test' });
    const trackedInput = makeTrackedElement('input-id-1', JSON.stringify(inputContext), 'input');
    trackedInput.setAttribute(TrackingAttribute.trackBlurs, 'true');
    jest.spyOn(trackedInput, 'addEventListener');

    trackNewElement(trackedInput, window.objectiv.tracker);

    expect(trackedInput.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedInput.addEventListener).toHaveBeenNthCalledWith(1, 'blur', expect.any(Function));
    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error');
    const inputContext = makeInputContext({ id: 'test' });
    const trackedInput = makeTrackedElement('input-id-1', JSON.stringify(inputContext), 'input');
    trackedInput.setAttribute(TrackingAttribute.trackBlurs, 'true');
    jest.spyOn(trackedInput, 'addEventListener').mockImplementation(() => {
      throw new Error('nope');
    });

    trackNewElement(trackedInput, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
