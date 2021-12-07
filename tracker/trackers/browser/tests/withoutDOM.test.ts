/*
 * Copyright 2021 Objectiv B.V.
 * @jest-environment node
 */

import { generateUUID, makeClickEvent } from '@objectiv/tracker-core';
import {
  BrowserTracker,
  DebugTransport,
  getLocationHref,
  getTracker,
  makeMutationCallback,
  makeTracker,
  startAutoTracking,
  trackAborted,
  trackApplicationLoaded,
  trackCompleted,
  TrackerQueueLocalStorage,
  trackEvent,
  trackURLChange,
} from '../src';

describe('Without DOM', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should throw if Window does not exists', async () => {
    expect(() => makeTracker({ applicationId: generateUUID(), transport: new DebugTransport() })).toThrow(
      'Cannot access the Window interface.'
    );

    expect(() => getTracker()).toThrow('Cannot access the Window interface.');
  });

  it('should console.error if a Tracker instance cannot be retrieved because DOM is not available', async () => {
    const parameters = { eventFactory: makeClickEvent, element: null };
    // @ts-ignore
    trackEvent(parameters);

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(1, Error('Cannot access the Window interface.'), parameters);
  });

  it('should console.error id Application Loaded Event fails at retrieving the document element', () => {
    trackApplicationLoaded();

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {});

    trackApplicationLoaded({ onError: console.error });
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should console.error id URL Change Event fails at retrieving the document element', () => {
    trackURLChange();

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {});

    trackURLChange({ onError: console.error });
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should console.error id Completed Event fails at retrieving the document element', () => {
    trackCompleted();

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {});

    trackCompleted({ onError: console.error });
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should console.error id Aborted Event fails at retrieving the document element', () => {
    trackAborted();

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {});

    trackAborted({ onError: console.error });
    expect(console.error).toHaveBeenCalledTimes(2);
    expect(console.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should return undefined', () => {
    expect(getLocationHref()).toBeUndefined();
  });

  it('should console error when MutationObserver is not available', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new BrowserTracker({ applicationId: 'app', transport: new DebugTransport() });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking();

    expect(tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should console error when mutationCallback receives garbled data', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new BrowserTracker({ applicationId: 'app', transport: new DebugTransport() });
    jest.spyOn(tracker, 'trackEvent');
    const mutationCallback = makeMutationCallback(false);

    // @ts-ignore
    mutationCallback('not a list');

    expect(tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });

  it('should throw if TrackerQueueLocalStorage gets constructed', async () => {
    expect(() => new TrackerQueueLocalStorage({ trackerId: 'app-id' })).toThrow(
      'TrackerQueueLocalStorage: failed to initialize: window.localStorage is not available.'
    );
  });
});
