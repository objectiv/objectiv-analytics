/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  ContextsConfig,
  generateGUID,
  GlobalContextName,
  makeHttpContext,
  Tracker,
  TrackerEvent,
} from '@objectiv/tracker-core';
import { HttpContextPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('HttpContextPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should TrackerConsole.error when calling `validate` before `initialize`', () => {
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
      id: generateGUID(),
      time: Date.now(),
    });
    testHttpContextPlugin.validate(validEvent);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:HttpContextPlugin｣ Cannot validate. Make sure to initialize the plugin first.'
    );
  });

  it('should add the HttpContext to the Event when `initialize` is executed by the Tracker', async () => {
    const originalReferrer = document.referrer;
    const originalUserAgent = navigator.userAgent;
    Object.defineProperty(document, 'referrer', { value: 'MOCK_REFERRER', configurable: true });
    Object.defineProperty(navigator, 'userAgent', { value: 'MOCK_USER_AGENT', configurable: true });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new HttpContextPlugin()],
    });
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'A' },
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'B' },
      ],
      global_contexts: [
        { __instance_id: generateGUID(), __global_context: true, _type: 'GlobalA', id: 'abc' },
        { __instance_id: generateGUID(), __global_context: true, _type: 'GlobalB', id: 'def' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts, id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(2);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(2);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.HttpContext,
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
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(0);
    expect(trackedEvent.global_contexts).toHaveLength(1);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.HttpContext,
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

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new HttpContextPlugin()],
    });

    it('should return silently  when calling `validate` before `initialize`', () => {
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
        id: generateGUID(),
        time: Date.now(),
      });
      testHttpContextPlugin.validate(validEvent);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should not validate', () => {
      const testHttpContextPlugin = new HttpContextPlugin();
      testHttpContextPlugin.initialize(testTracker);
      const eventWithDuplicatedHttpContext = new TrackerEvent({
        _type: 'TestEvent',
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
        id: generateGUID(),
        time: Date.now(),
      });

      jest.resetAllMocks();

      testHttpContextPlugin.validate(eventWithDuplicatedHttpContext);

      expect(MockConsoleImplementation.groupCollapsed).not.toHaveBeenCalled();
    });
  });
});
