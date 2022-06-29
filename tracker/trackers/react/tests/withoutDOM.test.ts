/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { ReactTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('Without DOM', () => {
  it('ReactTracker: should not instantiate LocalStorage but MemoryQueue instead', () => {
    expect(
      new ReactTracker({
        applicationId: 'app-id',
        endpoint: 'localhost',
      }).queue
    ).toEqual({
      queueName: 'TrackerQueue',
      batchDelayMs: 1000,
      batchSize: 10,
      concurrency: 4,
      lastRunTimestamp: 0,
      running: false,
      processingEventIds: [],
      store: {
        queueStoreName: 'TrackerQueueMemoryStore',
        events: [],
      },
    });
  });
});
