import { makeSectionContext, makeSectionHiddenEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, TrackingAttribute } from '../src';
import trackRemovedElements from '../src/observer/trackRemovedElements';
import makeTrackedElement from './mocks/makeTrackedElement';

describe('trackRemovedElements', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
  });

  it('should skip all Elements that are not Tracked Element', async () => {
    const div = document.createElement('div');
    const anotherDiv = document.createElement('div');
    const button = document.createElement('button');

    anotherDiv.appendChild(button);
    div.appendChild(anotherDiv);
    document.body.appendChild(div);

    trackRemovedElements(div, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should skip all Elements that do not have visibility tracking attributes', async () => {
    const trackedDiv = makeTrackedElement('div1', 'div1', 'div');
    const trackedChildDiv = makeTrackedElement('div2', 'div2', 'div');
    const trackedButton = makeTrackedElement('button', 'button', 'button');

    trackedDiv.appendChild(trackedChildDiv);
    trackedChildDiv.appendChild(trackedButton);
    document.body.appendChild(trackedDiv);

    trackRemovedElements(trackedDiv, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should trigger a visibility:hidden Event for Tracked Elements with visibility:auto attributes', async () => {
    const div = document.createElement('div');
    const sectionContext = makeSectionContext({ id: 'div' });
    const trackedDiv = makeTrackedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"auto"}');
    const trackedButton = makeTrackedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);
    document.body.appendChild(div);

    trackRemovedElements(div, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(
      1,
      makeSectionHiddenEvent({ location_stack: [sectionContext] })
    );
  });

  it('should not trigger a visibility:hidden Event for Tracked Elements with visibility:manual attributes', async () => {
    const div = document.createElement('div');
    const trackedDiv = makeTrackedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');
    const trackedButton = makeTrackedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);
    document.body.appendChild(div);

    trackRemovedElements(div, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error');
    const div = document.createElement('div');
    const trackedDiv = makeTrackedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TrackingAttribute.trackVisibility, '{"mode":"broken"}');
    const trackedButton = makeTrackedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);
    document.body.appendChild(div);

    trackRemovedElements(div, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error');
    const div = document.createElement('div');
    jest.spyOn(div, 'querySelectorAll').mockImplementation(() => {
      throw new Error();
    });

    trackRemovedElements(div, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
