/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { ContextsConfig, generateGUID, GlobalContextName, Tracker, TrackerEvent } from '@objectiv/tracker-core';
import { PathContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

const testTracker = new Tracker({
  applicationId: 'app-id',
  plugins: [new PathContextFromURLPlugin()],
});

describe('PathContextFromURLPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should add the PathContext to the Event when `enrich` is executed by the Tracker', async () => {
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
          _type: GlobalContextName.PathContext,
          id: 'http://localhost/',
        },
      ])
    );
  });
});
