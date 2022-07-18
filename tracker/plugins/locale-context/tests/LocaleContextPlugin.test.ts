/*
 * Copyright 2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, GlobalContextName, Tracker, TrackerEvent } from '@objectiv/tracker-core';
import { LocaleContextPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocaleContextPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not add the LocaleContext to the Event when `enrich` is executed by the Tracker', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new LocaleContextPlugin({
          idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
        }),
      ],
    });

    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(0);
    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '｢objectiv:LocaleContextPlugin｣ Cannot enrich. Could not determine locale.'
    );
  });

  it('should add the LocaleContext to the Event when `enrich` is executed by the Tracker', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/en/home',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new LocaleContextPlugin({
          idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
        }),
      ],
    });

    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(1);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.LocaleContext,
          id: 'en',
        },
      ])
    );
  });
});
