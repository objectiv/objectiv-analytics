/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  ContextsConfig,
  generateUUID,
  GlobalContextName,
  makePathContext,
  Tracker,
  TrackerEvent,
} from '@objectiv/tracker-core';
import { PathContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

const testTracker = new Tracker({
  applicationId: 'app-id',
  plugins: [new PathContextFromURLPlugin()],
  trackApplicationContext: false,
});

describe('PathContextFromURLPlugin', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  it('should TrackerConsole.error when calling `validate` before `initialize`', () => {
    const testPathContextPlugin = new PathContextFromURLPlugin();
    const validEvent = new TrackerEvent({
      _type: 'test',
      global_contexts: [makePathContext({ id: '/test' })],
    });
    testPathContextPlugin.validate(validEvent);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:PathContextFromURLPlugin｣ Cannot validate. Make sure to initialize the plugin first.'
    );
  });

  it('should add the PathContext to the Event when `enrich` is executed by the Tracker', async () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'A' },
        { __instance_id: generateUUID(), __location_context: true, _type: 'section', id: 'B' },
      ],
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'GlobalA', id: 'abc' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'GlobalB', id: 'def' },
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
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.PathContext,
          id: 'http://localhost/',
        },
      ])
    );
  });

  it('should fail when given TrackerEvent does not have PathContext', () => {
    const testPathContextPlugin = new PathContextFromURLPlugin();
    testPathContextPlugin.initialize(testTracker);
    const eventWithoutPathContext = new TrackerEvent({ _type: 'TestEvent' });

    jest.resetAllMocks();

    testPathContextPlugin.validate(eventWithoutPathContext);

    expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:PathContextFromURLPlugin｣ Error: PathContext is missing from Global Contexts of TestEvent.\n' +
        'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      'color:red'
    );
  });

  it('should fail when given TrackerEvent has multiple PathContexts', () => {
    const testPathContextPlugin = new PathContextFromURLPlugin();
    testPathContextPlugin.initialize(testTracker);
    const eventWithDuplicatedPathContext = new TrackerEvent({
      _type: 'TestEvent',
      global_contexts: [makePathContext({ id: '/test' }), makePathContext({ id: '/test' })],
    });

    jest.resetAllMocks();

    testPathContextPlugin.validate(eventWithDuplicatedPathContext);

    expect(MockConsoleImplementation.groupCollapsed).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.groupCollapsed).toHaveBeenNthCalledWith(
      1,
      '%c｢objectiv:PathContextFromURLPlugin｣ Error: Only one PathContext should be present in Global Contexts of TestEvent.\n' +
        'Taxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      'color:red'
    );
  });
});

describe('Without developer tools', () => {
  let objectivGlobal = globalThis.objectiv;

  beforeEach(() => {
    jest.clearAllMocks();
    globalThis.objectiv = undefined;
  });

  afterEach(() => {
    globalThis.objectiv = objectivGlobal;
  });

  it('should return silently when calling `validate` before `initialize`', () => {
    const testPathContextPlugin = new PathContextFromURLPlugin();
    const validEvent = new TrackerEvent({
      _type: 'test',
      global_contexts: [makePathContext({ id: '/test' })],
    });
    testPathContextPlugin.validate(validEvent);
    expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
  });

  it('should not log anything on successful initialization', () => {
    const testPathContextPlugin = new PathContextFromURLPlugin();
    testPathContextPlugin.initialize(testTracker);

    expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
  });
});
