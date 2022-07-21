/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeMutationCallback, TaggingAttribute } from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('makeMutationCallback - new nodes', () => {
  afterEach(() => {
    getTrackerRepository().delete('test-app');
  });

  it('should track newly added nodes that are Elements and visibility for existing nodes', () => {
    const tracker = new BrowserTracker({ transport: new LogTransport(), applicationId: 'test-app' });
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
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' })],
      })
    );
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'VisibleEvent',
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
    const tracker = new BrowserTracker({ transport: new LogTransport(), applicationId: 'app' });
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
