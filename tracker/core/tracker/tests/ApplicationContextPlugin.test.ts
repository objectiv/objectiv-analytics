/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  ApplicationContextPlugin,
  ContextsConfig,
  generateUUID,
  GlobalContextName,
  Tracker,
  TrackerEvent,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

const coreTracker = new Tracker({ applicationId: 'app-id' });

describe('ApplicationContextPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('should generate an ApplicationContext when initialized', () => {
    expect(coreTracker.plugins.get('ApplicationContextPlugin')).toEqual(
      expect.objectContaining({
        applicationContext: {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.ApplicationContext,
          id: 'app-id',
        },
      })
    );
  });

  it('should TrackerConsole.error when calling `enrich` before `initialize`', () => {
    const testApplicationContextPlugin = new ApplicationContextPlugin();
    testApplicationContextPlugin.enrich({ location_stack: [], global_contexts: [] });
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv:ApplicationContextPlugin｣ Cannot enrich. Make sure to initialize the plugin first.'
    );
  });

  it('should add the ApplicationContext to the Event when `enrich` is executed by the Tracker', async () => {
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const trackedEvent = await coreTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.ApplicationContext,
          id: 'app-id',
        },
      ])
    );
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

    it('should return silently when calling `enrich` before `initialize`', () => {
      const testApplicationContextPlugin = new ApplicationContextPlugin();
      testApplicationContextPlugin.enrich({ location_stack: [], global_contexts: [] });
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
