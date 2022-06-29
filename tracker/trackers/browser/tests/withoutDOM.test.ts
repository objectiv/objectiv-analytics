/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { DebugTransport } from '@objectiv/transport-debug';
import {
  getLocationHref,
  makeTracker,
  startAutoTracking,
  trackApplicationLoadedEvent,
  trackFailureEvent,
  trackSuccessEvent,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('Without DOM', () => {
  beforeEach(() => {
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should TrackerConsole.error id Application Loaded Event fails at retrieving the document element', () => {
    trackApplicationLoadedEvent();

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      new ReferenceError('document is not defined'),
      {}
    );

    trackApplicationLoadedEvent({ onError: MockConsoleImplementation.error });
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should TrackerConsole.error id Completed Event fails at retrieving the document element', () => {
    trackSuccessEvent({ message: 'ok' });

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {
      message: 'ok',
    });

    trackSuccessEvent({ message: 'ok', onError: MockConsoleImplementation.error });
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should TrackerConsole.error id Aborted Event fails at retrieving the document element', () => {
    trackFailureEvent({ message: 'ko' });

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(1, new ReferenceError('document is not defined'), {
      message: 'ko',
    });

    trackFailureEvent({ message: 'ko', onError: MockConsoleImplementation.error });
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(2, new ReferenceError('document is not defined'));
  });

  it('should return undefined', () => {
    expect(getLocationHref()).toBeUndefined();
  });

  it('should TrackerConsole.error when MutationObserver is not available', async () => {
    const tracker = makeTracker({ applicationId: 'app', transport: new DebugTransport() });
    jest.spyOn(tracker, 'trackEvent');

    startAutoTracking();

    expect(tracker.trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      ReferenceError('MutationObserver is not defined'),
      undefined
    );
  });
});
