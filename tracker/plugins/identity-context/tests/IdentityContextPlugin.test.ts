/*
 * Copyright 2022 Objectiv B.V.
 */

import { IdentityContextPlugin } from '@objectiv/plugin-identity-context';
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { ContextsConfig, generateUUID, GlobalContextName, Tracker, TrackerEvent } from '@objectiv/tracker-core';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('IdentityContextPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should allow configuring the IdentityContext attributes by value', async () => {
    const identityContextPlugin = new IdentityContextPlugin({
      id: 'backend',
      value: 'test',
    });
    expect(identityContextPlugin).toBeInstanceOf(IdentityContextPlugin);
    expect(identityContextPlugin.config).toStrictEqual({
      id: 'backend',
      value: 'test',
    });
  });

  it('should allow configuring the IdentityContext attributes by value array', async () => {
    const identityContextPlugin = new IdentityContextPlugin([
      {
        id: 'backend',
        value: 'test 1',
      },
      {
        id: 'authentication',
        value: 'test 2',
      },
    ]);
    expect(identityContextPlugin).toBeInstanceOf(IdentityContextPlugin);
    expect(identityContextPlugin.config).toStrictEqual([
      {
        id: 'backend',
        value: 'test 1',
      },
      {
        id: 'authentication',
        value: 'test 2',
      },
    ]);
  });

  it('should allow configuring the IdentityContext attributes by function returning an object', async () => {
    const identityContextPlugin = new IdentityContextPlugin(() => ({
      id: 'backend',
      value: 'test',
    }));
    expect(identityContextPlugin).toBeInstanceOf(IdentityContextPlugin);
    expect(identityContextPlugin.config).toBeInstanceOf(Function);
  });

  it('should allow configuring the IdentityContext attributes by function returning an array of objects', async () => {
    const identityContextPlugin = new IdentityContextPlugin(() => [
      {
        id: 'backend',
        value: 'test 1',
      },
      {
        id: 'authentication',
        value: 'test 2',
      },
    ]);
    expect(identityContextPlugin).toBeInstanceOf(IdentityContextPlugin);
    expect(identityContextPlugin.config).toBeInstanceOf(Function);
  });

  it('should add one IdentityContext - config by value', async () => {
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const coreTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new IdentityContextPlugin({
          id: 'backend',
          value: 'test 1',
        }),
      ],
    });
    const trackedEvent = await coreTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(4);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'backend',
          value: 'test 1',
        }),
      ])
    );
  });

  it('should add two IdentityContexts - config by array of values', async () => {
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const coreTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new IdentityContextPlugin([
          {
            id: 'backend',
            value: 'test 1',
          },
          {
            id: 'authentication',
            value: 'test 2',
          },
        ]),
      ],
    });
    const trackedEvent = await coreTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(5);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'backend',
          value: 'test 1',
        }),
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'authentication',
          value: 'test 2',
        }),
      ])
    );
  });

  it('should add one IdentityContexts - config by function returning a single object', async () => {
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const coreTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new IdentityContextPlugin(() => ({
          id: 'backend',
          value: 'test 1',
        })),
      ],
    });

    const trackedEvent = await coreTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(4);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'backend',
          value: 'test 1',
        }),
      ])
    );
  });

  it('should add one IdentityContexts - config by function returning an array of objects', async () => {
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'X' },
        { __instance_id: generateUUID(), __global_context: true, _type: 'Context', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const coreTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new IdentityContextPlugin(() => [
          {
            id: 'backend',
            value: 'test 1',
          },
          {
            id: 'authentication',
            value: 'test 2',
          },
        ]),
      ],
    });

    const trackedEvent = await coreTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(5);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'backend',
          value: 'test 1',
        }),
        expect.objectContaining({
          _type: GlobalContextName.IdentityContext,
          id: 'authentication',
          value: 'test 2',
        }),
      ])
    );
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

    it('should not log', () => {
      new IdentityContextPlugin({
        id: 'backend',
        value: 'test',
      });
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });
  });
});
