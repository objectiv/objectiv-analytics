/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { ContextsConfig, makeHttpContext, Tracker, TrackerConsole, TrackerEvent } from '@objectiv/tracker-core';
import { HttpContextPlugin } from '../src';

TrackerConsole.setImplementation(MockConsoleImplementation);

describe('HttpContextPlugin', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  it('should add the HttpContext to the Event when `initialize` is executed by the Tracker', async () => {
    const originalReferrer = document.referrer;
    const originalUserAgent = navigator.userAgent;
    Object.defineProperty(document, 'referrer', { value: 'MOCK_REFERRER', configurable: true });
    Object.defineProperty(navigator, 'userAgent', { value: 'MOCK_USER_AGENT', configurable: true });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new HttpContextPlugin()],
      trackApplicationContext: false,
    });
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __location_context: true, _type: 'section', id: 'A' },
        { __location_context: true, _type: 'section', id: 'B' },
      ],
      global_contexts: [
        { __global_context: true, _type: 'GlobalA', id: 'abc' },
        { __global_context: true, _type: 'GlobalB', id: 'def' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.location_stack).toHaveLength(2);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(2);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __global_context: true,
          _type: 'HttpContext',
          id: 'http_context',
          referrer: 'MOCK_REFERRER',
          remote_address: null,
          user_agent: 'MOCK_USER_AGENT',
        },
      ])
    );

    Object.defineProperty(document, 'referrer', { value: originalReferrer });
    Object.defineProperty(navigator, 'userAgent', { value: originalUserAgent });
  });

  it('should default to empty strings for referrer and user_agent, whenever they are null', async () => {
    const originalReferrer = document.referrer;
    const originalUserAgent = navigator.userAgent;
    Object.defineProperty(document, 'referrer', { value: null, configurable: true });
    Object.defineProperty(navigator, 'userAgent', { value: null, configurable: true });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new HttpContextPlugin()],
      trackApplicationContext: false,
    });
    const testEvent = new TrackerEvent({ _type: 'test-event' });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(0);
    expect(trackedEvent.global_contexts).toHaveLength(1);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __global_context: true,
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          remote_address: null,
          user_agent: '',
        },
      ])
    );

    Object.defineProperty(document, 'referrer', { value: originalReferrer });
    Object.defineProperty(navigator, 'userAgent', { value: originalUserAgent });
  });

  describe('Validation', () => {
    it('should succeed', () => {
      const testHttpContextPlugin = new HttpContextPlugin();
      const validEvent = new TrackerEvent({
        _type: 'test',
        global_contexts: [
          makeHttpContext({
            id: '/test',
            user_agent: 'test',
            referrer: 'test',
            remote_address: 'test',
          }),
        ],
      });

      jest.resetAllMocks();

      testHttpContextPlugin.validate(validEvent);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });

    it('should fail when given TrackerEvent does not have HttpContext', () => {
      const testHttpContextPlugin = new HttpContextPlugin();
      const eventWithoutHttpContext = new TrackerEvent({ _type: 'test' });

      jest.resetAllMocks();

      testHttpContextPlugin.validate(eventWithoutHttpContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        `%c｢objectiv:HttpContextPlugin:GlobalContextValidationRule｣ Error: HttpContext is missing from Global Contexts.`,
        'color:red'
      );
    });

    it('should fail when given TrackerEvent has multiple HttpContexts', () => {
      const testHttpContextPlugin = new HttpContextPlugin();
      const eventWithDuplicatedHttpContext = new TrackerEvent({
        _type: 'test',
        global_contexts: [
          makeHttpContext({
            id: '/test',
            user_agent: 'test',
            referrer: 'test',
            remote_address: 'test',
          }),
          makeHttpContext({
            id: '/test',
            user_agent: 'test',
            referrer: 'test',
            remote_address: 'test',
          }),
        ],
      });

      jest.resetAllMocks();

      testHttpContextPlugin.validate(eventWithDuplicatedHttpContext);

      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
        1,
        `%c｢objectiv:HttpContextPlugin:GlobalContextValidationRule｣ Error: Only one HttpContext should be present in Global Contexts.`,
        'color:red'
      );
    });
  });
});
