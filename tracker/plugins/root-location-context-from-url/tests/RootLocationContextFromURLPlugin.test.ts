/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { ContextsConfig, generateGUID, LocationContextName, Tracker, TrackerEvent } from '@objectiv/tracker-core';
import { RootLocationContextFromURLPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('RootLocationContextFromURLPlugin', () => {
  beforeEach(() => {
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should add the RootLocationContext to the Event when `enrich` is executed by the Tracker', async () => {
    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin()],
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
    expect(trackedEvent.location_stack).toHaveLength(3);
    expect(trackedEvent.location_stack[0]).toEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'home',
    });
    expect(trackedEvent.global_contexts).toHaveLength(2);
  });

  it('should add the RootLocationContext with id: home', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin()],
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(1);
    expect(trackedEvent.location_stack[0]).toEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'home',
    });
  });

  it('should add the RootLocationContext with id: home', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin()],
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(1);
    expect(trackedEvent.location_stack[0]).toEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'home',
    });
  });

  it('should add the RootLocationContext with id: dashboard', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/dashboard/some/more/slugs',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin()],
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(1);
    expect(trackedEvent.location_stack[0]).toEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'dashboard',
    });
  });

  it('should console.error', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        // Can't really happen, but just to test this case
        pathname: null,
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin()],
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(0);
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      `%c｢objectiv:RootLocationContextFromURLPlugin｣ Could not generate a RootLocationContext from "null"`,
      `font-weight: bold`
    );
  });

  it('should allow overriding the id factory function', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        href: 'https://spa.app#welcome',
      },
      writable: true,
    });

    const makeRootLocationIdFromHash = () => location.href?.split('#')[1].trim().toLowerCase();

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [new RootLocationContextFromURLPlugin({ idFactoryFunction: makeRootLocationIdFromHash })],
    });
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.location_stack).toHaveLength(0);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.location_stack).toHaveLength(1);
    expect(trackedEvent.location_stack[0]).toEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'welcome',
    });
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

    it('should not console.error', async () => {
      Object.defineProperty(window, 'location', {
        value: {
          // Can't really happen, but just to test this case
          pathname: null,
        },
        writable: true,
      });

      const testTracker = new Tracker({
        applicationId: 'app-id',
        plugins: [new RootLocationContextFromURLPlugin()],
      });
      const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
      expect(testEvent.location_stack).toHaveLength(0);
      const trackedEvent = await testTracker.trackEvent(testEvent);
      expect(trackedEvent.location_stack).toHaveLength(0);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
