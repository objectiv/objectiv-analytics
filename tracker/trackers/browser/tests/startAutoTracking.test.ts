/*
 * Copyright 2021 Objectiv B.V.
 */

import { generateUUID } from '@objectiv/tracker-core';
import {
  AutoTrackingState,
  BrowserTracker,
  getTracker,
  getTrackerRepository,
  makeMutationCallback,
  makeTracker,
  startAutoTracking,
  stopAutoTracking,
  TaggingAttribute,
} from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';
import { matchUUID } from './mocks/matchUUID';

describe('startAutoTracking', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('options', () => {
    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true, trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({ trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: true, trackURLChanges: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: true });
    stopAutoTracking();
    startAutoTracking({});
    stopAutoTracking();
    startAutoTracking();
    stopAutoTracking();
    stopAutoTracking();
  });

  it('should console.error', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    startAutoTracking();
    expect(console.error).not.toHaveBeenCalled();
    // @ts-ignore
    AutoTrackingState.observerInstance = {
      disconnect: () => {
        throw new Error('oops');
      },
    };
    stopAutoTracking();
    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should not track application loaded event', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking({ trackApplicationLoaded: false, trackURLChanges: false });

    expect(tracker.trackEvent).not.toHaveBeenCalled();
  });
});

describe('makeMutationCallback - url changes', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should not track url changes', () => {
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost/new-url',
      },
      writable: true,
    });
    mutationCallback([], mutationObserver);

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track url changes only urls change', () => {
    const mutationCallback = makeMutationCallback(true);
    const mutationObserver = new MutationObserver(mutationCallback);

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost/',
      },
      writable: true,
    });
    AutoTrackingState.previousURL = 'http://localhost/';

    mutationCallback([], mutationObserver);

    expect(getTracker().trackEvent).not.toHaveBeenCalled();

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost/another-url',
      },
      writable: true,
    });
    mutationCallback([], mutationObserver);

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'URLChangeEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [],
      })
    );
  });
});

describe('makeMutationCallback - new nodes', () => {
  it('should track newly added nodes that are Elements and visibility for existing nodes', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    const trackerRepository = getTrackerRepository();
    trackerRepository.add(tracker);
    trackerRepository.setDefault(tracker.trackerId);
    jest.spyOn(tracker, 'trackEvent');
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    const mockedMutationRecord: MutationRecord = {
      // @ts-ignore
      addedNodes: [document.createComment('comment'), trackedDiv],
      // @ts-ignore
      removedNodes: [document.createComment('comment')],
      attributeName: TaggingAttribute.trackVisibility,
      target: trackedDiv,
    };
    mutationCallback([mockedMutationRecord], mutationObserver);

    expect(tracker.trackEvent).toHaveBeenCalledTimes(2);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'SectionVisibleEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [
          {
            _type: 'SectionContext',
            id: 'div',
          },
        ],
      })
    );
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'SectionVisibleEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [
          {
            _type: 'SectionContext',
            id: 'div',
          },
        ],
      })
    );
  });

  it('should console.error if there are no Trackers', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    getTrackerRepository().trackersMap = new Map();
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    const mockedMutationRecord: MutationRecord = {
      // @ts-ignore
      addedNodes: [trackedDiv],
      // @ts-ignore
      removedNodes: [],
      attributeName: TaggingAttribute.trackVisibility,
      target: trackedDiv,
    };
    jest.clearAllMocks();
    expect(console.error).not.toHaveBeenCalled();
    mutationCallback([mockedMutationRecord], mutationObserver);
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(1, `｢objectiv:TrackerRepository｣ There are no Trackers.`);
    expect(console.error).toHaveBeenNthCalledWith(
      2,
      new Error(`No Tracker found. Please create one via \`makeTracker\`.`),
      undefined
    );
  });
});

describe('makeMutationCallback - removed nodes', () => {
  it('should track visibility:hidden events for removed nodes', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    const trackerRepository = getTrackerRepository();
    trackerRepository.add(tracker);
    trackerRepository.setDefault(tracker.trackerId);
    jest.spyOn(tracker, 'trackEvent');
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    const mockedMutationRecord: MutationRecord = {
      // @ts-ignore
      addedNodes: [],
      // @ts-ignore
      removedNodes: [trackedDiv],
    };
    mutationCallback([mockedMutationRecord], mutationObserver);

    expect(tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'SectionHiddenEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [
          {
            _type: 'SectionContext',
            id: 'div',
          },
        ],
      })
    );
  });
});

describe('makeMutationCallback - attribute changes', () => {
  it('should remove element from TrackerElementLocations when its id changes', () => {
    const mutationCallback = makeMutationCallback(false);
    const mutationObserver = new MutationObserver(mutationCallback);

    const trackedDiv = makeTaggedElement('div', 'div', 'div');

    const oldValue = 'old-id';
    const mockedMutationRecord: MutationRecord = {
      attributeNamespace: null,
      nextSibling: null,
      previousSibling: null,
      // @ts-ignore
      addedNodes: [],
      // @ts-ignore
      removedNodes: [],
      type: 'attributes',
      // @ts-ignore
      target: trackedDiv,
      attributeName: TaggingAttribute.elementId,
      oldValue,
    };
    mutationCallback([mockedMutationRecord], mutationObserver);
  });
});
