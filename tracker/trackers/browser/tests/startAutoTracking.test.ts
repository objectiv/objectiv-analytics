/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import '@objectiv/developer-tools';
import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateUUID, LocationContextName } from '@objectiv/tracker-core';
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

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('startAutoTracking', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('options', () => {
    startAutoTracking({ trackApplicationLoadedEvent: false });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoadedEvent: true });
    stopAutoTracking();
    startAutoTracking({ trackApplicationLoadedEvent: false });
    stopAutoTracking();
    startAutoTracking({});
    stopAutoTracking();
    startAutoTracking();
    stopAutoTracking();
    stopAutoTracking();
  });

  it('should TrackerConsole.error', () => {
    startAutoTracking();
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    // @ts-ignore
    AutoTrackingState.observerInstance = {
      disconnect: () => {
        throw new Error('oops');
      },
    };
    stopAutoTracking();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  it('should not track application loaded event', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking({ trackApplicationLoadedEvent: false });

    expect(tracker.trackEvent).not.toHaveBeenCalled();
  });
});

describe('makeMutationCallback - new nodes', () => {
  it('should track newly added nodes that are Elements and visibility for existing nodes', () => {
    const tracker = new BrowserTracker({ endpoint: 'endpoint', applicationId: 'app' });
    const trackerRepository = getTrackerRepository();
    trackerRepository.add(tracker);
    trackerRepository.setDefault(tracker.trackerId);
    jest.spyOn(tracker, 'trackEvent');
    const mutationCallback = makeMutationCallback();
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
        _type: 'VisibleEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' })],
      })
    );
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'VisibleEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' })],
      })
    );
  });

  it('should TrackerConsole.error if there are no Trackers', () => {
    getTrackerRepository().trackersMap = new Map();
    const mutationCallback = makeMutationCallback();
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
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    mutationCallback([mockedMutationRecord], mutationObserver);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      `｢objectiv:TrackerRepository｣ There are no Trackers.`
    );
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
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
    const mutationCallback = makeMutationCallback();
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
        _type: 'HiddenEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' })],
      })
    );
  });
});

describe('makeMutationCallback - attribute changes', () => {
  it('should remove element from TrackerElementLocations when its id changes', () => {
    const mutationCallback = makeMutationCallback();
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

    jest.spyOn(document, 'querySelector').mockReturnValueOnce(trackedDiv);

    mutationCallback([mockedMutationRecord], mutationObserver);

    expect(document.querySelector).toHaveBeenCalledTimes(1);
    expect(document.querySelector).toHaveBeenNthCalledWith(1, `[${TaggingAttribute.elementId}='old-id']`);
  });
});
