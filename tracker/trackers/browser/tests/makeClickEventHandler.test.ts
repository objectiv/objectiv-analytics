/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  generateGUID,
  LocationContextName,
  makePressEvent,
  TrackerQueue,
  TrackerQueueMemoryStore,
} from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker, trackPressEvent } from '../src/';
import { makeClickEventHandler } from '../src/mutationObserver/makeClickEventHandler';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('makeClickEventHandler', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({
      applicationId: generateGUID(),
      endpoint: 'test',
      queue: new TrackerQueue({ store: new TrackerQueueMemoryStore(), batchDelayMs: 1 }),
    });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
  });

  it('should track Button Click when invoked from a valid target', () => {
    const trackedButton = makeTaggedElement('button', null, 'button');
    const clickEventListener = makeClickEventHandler(trackedButton, getTracker());

    trackedButton.addEventListener('click', clickEventListener);
    trackedButton.dispatchEvent(new MouseEvent('click'));

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should not track Div Click when invoked from a bubbling target', () => {
    const trackedButton = makeTaggedElement('button', null, 'button');
    const trackedDiv = makeTaggedElement('div', null, 'div');
    const divClickEventListener = jest.fn(makeClickEventHandler(trackedDiv, getTracker()));

    trackedDiv.addEventListener('click', divClickEventListener);
    trackedButton.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(divClickEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track Div Click when current target is not a click-tracking tagged element', () => {
    const span = document.createElement('span');
    const trackedButton = makeTaggedElement('button', 'button', 'button', false);
    trackedButton.appendChild(span);
    const buttonClickEventListener = jest.fn(makeClickEventHandler(trackedButton, getTracker()));

    trackedButton.addEventListener('click', buttonClickEventListener);
    span.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(buttonClickEventListener).toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track Div Click when invoked from a non-tagged child', () => {
    const span = document.createElement('span');
    const trackedButton = makeTaggedElement('button', 'button', 'button', true);
    trackedButton.appendChild(span);
    const buttonClickEventListener = jest.fn(makeClickEventHandler(trackedButton, getTracker()));

    trackedButton.addEventListener('click', buttonClickEventListener);
    span.dispatchEvent(new MouseEvent('click', { bubbles: true }));

    expect(buttonClickEventListener).toHaveBeenCalled();
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining(
        makePressEvent({
          location_stack: [expect.objectContaining({ _type: LocationContextName.PressableContext, id: 'button' })],
        })
      )
    );
  });

  it('should waitUntilTracked', async () => {
    jest.spyOn(getTracker(), 'flushQueue');
    const trackedButton = makeTaggedElement('button', null, 'button');
    const clickEventListener = makeClickEventHandler(trackedButton, getTracker(), {
      flushQueue: true,
      waitForQueue: { timeoutMs: 1, intervalMs: 1 },
    });

    const mockEvent = {
      ...new Event('click'),
      preventDefault: jest.fn(),
      stopImmediatePropagation: jest.fn(),
    };
    mockEvent.constructor = Event;

    await clickEventListener({ ...mockEvent, target: trackedButton });
    expect(getTracker().flushQueue).toHaveBeenCalled();
  });

  it('should flush the queue - explicit setting', async () => {
    jest.spyOn(getTracker(), 'flushQueue');
    const trackedButton = makeTaggedElement('button', null, 'button');
    const clickEventListener = makeClickEventHandler(trackedButton, getTracker(), {
      flushQueue: true,
      waitForQueue: {
        timeoutMs: 1,
        intervalMs: 1,
      },
    });

    const mockEvent = {
      ...new Event('click'),
      preventDefault: jest.fn(),
      stopImmediatePropagation: jest.fn(),
    };
    mockEvent.constructor = Event;

    await clickEventListener({ ...mockEvent, target: trackedButton });
    expect(getTracker().flushQueue).toHaveBeenCalled();
  });

  it('should flush the queue - onTimeout', async () => {
    jest.spyOn(getTracker(), 'flushQueue');
    const trackedButton = makeTaggedElement('button', null, 'button');
    const clickEventListener = makeClickEventHandler(trackedButton, getTracker(), {
      flushQueue: 'onTimeout',
    });

    const mockEvent = {
      ...new Event('click'),
      preventDefault: jest.fn(),
      stopImmediatePropagation: jest.fn(),
    };
    mockEvent.constructor = Event;

    trackPressEvent({ element: trackedButton, tracker: getTracker() });
    await clickEventListener({ ...mockEvent, target: trackedButton });
    // FIXME This cannot be tested: JSDOM crashes. Seems to be a problem with timers in promises and Jest.
  });

  it('should not flush the queue', async () => {
    jest.spyOn(getTracker(), 'flushQueue');
    const trackedButton = makeTaggedElement('button', null, 'button');
    const clickEventListener = makeClickEventHandler(trackedButton, getTracker(), {
      flushQueue: false,
      waitForQueue: {
        timeoutMs: 1,
        intervalMs: 1,
      },
    });

    const mockEvent = {
      ...new Event('click'),
      preventDefault: jest.fn(),
      stopImmediatePropagation: jest.fn(),
    };
    mockEvent.constructor = Event;

    await clickEventListener({ ...mockEvent, target: trackedButton });
    expect(getTracker().flushQueue).not.toHaveBeenCalled();
  });
});
