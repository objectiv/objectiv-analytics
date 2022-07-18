/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { generateGUID, TrackerEvent, TrackerQueue, TrackerQueueMemoryStore } from '../src';

describe('TrackerQueueMemoryStore', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const TrackerEvent1 = new TrackerEvent({ id: 'a', _type: 'a', time: Date.now() });
  const TrackerEvent2 = new TrackerEvent({ id: 'b', _type: 'b', time: Date.now() });
  const TrackerEvent3 = new TrackerEvent({ id: 'c', _type: 'c', time: Date.now() });

  it('should read all Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    const events = await trackerQueueStore.read();

    expect(events.map((event) => event._type)).toStrictEqual(['a', 'b', 'c']);
  });

  it('should read 2 Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    const events = await trackerQueueStore.read(2);

    expect(events.map((event) => event._type)).toStrictEqual(['a', 'b']);
  });

  it('should allow filtering when reading Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    const events = await trackerQueueStore.read(Infinity, (event) => event._type !== 'a');

    expect(events.map((event) => event._type)).toStrictEqual(['b', 'c']);
  });

  it('should delete Events matching the given ids', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    await trackerQueueStore.delete(['a', 'c']);

    expect(trackerQueueStore.events.map((event) => event._type)).toStrictEqual(['b']);
    expect(trackerQueueStore.length).toBe(1);
  });

  it('should delete all Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    await trackerQueueStore.clear();

    expect(trackerQueueStore.events).toStrictEqual([]);
    expect(trackerQueueStore.length).toBe(0);
  });
});

describe('TrackerQueue', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  const TrackerEvent1 = new TrackerEvent({ _type: 'a', id: generateGUID(), time: Date.now() });
  const TrackerEvent2 = new TrackerEvent({ _type: 'b', id: generateGUID(), time: Date.now() });
  const TrackerEvent3 = new TrackerEvent({ _type: 'c', id: generateGUID(), time: Date.now() });

  it('should instantiate to a 0 length Queue', () => {
    const testQueue = new TrackerQueue({ batchDelayMs: 1 });
    expect(testQueue.store.length).toBe(0);
  });

  it('should allow enqueuing multiple items at once', () => {
    const testQueue = new TrackerQueue({ batchDelayMs: 1 });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    testQueue.setProcessFunction(processFunctionSpy);
    testQueue.push(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(testQueue.store.length).toBe(3);
  });

  it('should allow setting batchSize and batchDelayMs', () => {
    const testQueue = new TrackerQueue({ batchSize: 123, batchDelayMs: 456 });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    testQueue.setProcessFunction(processFunctionSpy);
    expect(testQueue.batchSize).toBe(123);
    expect(testQueue.batchDelayMs).toBe(456);
  });

  it('should throw an exception if the processFunction has not been set', async () => {
    const testQueue = new TrackerQueue({ batchSize: 1, batchDelayMs: 1 });
    await expect(testQueue.run()).rejects.toBe('TrackerQueue `processFunction` has not been set.');
  });

  it('should enqueue and dequeue in the expected order', async () => {
    const memoryStore = new TrackerQueueMemoryStore();
    const testQueue = new TrackerQueue({
      batchSize: 1,
      concurrency: 1,
      store: memoryStore,
      batchDelayMs: 1,
    });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    testQueue.setProcessFunction(processFunctionSpy);
    expect(testQueue.store.length).toBe(0);

    await testQueue.push(TrackerEvent1, TrackerEvent2, TrackerEvent3);

    expect(processFunctionSpy).toHaveBeenCalledTimes(3);
    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent1);
    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent2);
    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent3);
    expect(memoryStore.length).toBe(0);
  });

  it('should support batches', async () => {
    const testQueue = new TrackerQueue({ batchSize: 2, concurrency: 1, batchDelayMs: 1 });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    testQueue.setProcessFunction(processFunctionSpy);
    await testQueue.push(TrackerEvent1, TrackerEvent2, TrackerEvent3);

    expect(processFunctionSpy).toHaveBeenCalledTimes(2);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(1, TrackerEvent1, TrackerEvent2);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(2, TrackerEvent3);
    expect(testQueue.store.length).toBe(0);
    expect(testQueue.processingEventIds).toHaveLength(0);
  });

  it('should support concurrent batches', async () => {
    const TrackerEvent4 = new TrackerEvent({ _type: 'd', id: generateGUID(), time: Date.now() });
    const TrackerEvent5 = new TrackerEvent({ _type: 'e', id: generateGUID(), time: Date.now() });
    const TrackerEvent6 = new TrackerEvent({ _type: 'f', id: generateGUID(), time: Date.now() });
    const TrackerEvent7 = new TrackerEvent({ _type: 'g', id: generateGUID(), time: Date.now() });
    const testQueue = new TrackerQueue({ batchSize: 3, concurrency: 3, batchDelayMs: 1 });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    testQueue.setProcessFunction(processFunctionSpy);
    await testQueue.push(
      TrackerEvent1,
      TrackerEvent2,
      TrackerEvent3,
      TrackerEvent4,
      TrackerEvent5,
      TrackerEvent6,
      TrackerEvent7
    );

    expect(processFunctionSpy).toHaveBeenCalledTimes(3);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(1, ...[TrackerEvent1, TrackerEvent2, TrackerEvent3]);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(2, ...[TrackerEvent4, TrackerEvent5, TrackerEvent6]);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(3, ...[TrackerEvent7]);
    expect(testQueue.store.length).toBe(0);
    expect(testQueue.processingEventIds).toHaveLength(0);
  });

  it('should flush pending events', async () => {
    const testQueue = new TrackerQueue({ batchSize: 3, concurrency: 3, batchDelayMs: 1 });
    await testQueue.store.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(testQueue.store.length).toBe(3);
    expect(testQueue.isIdle()).toBe(false);

    await testQueue.flush();

    expect(testQueue.store.length).toBe(0);
    expect(testQueue.isIdle()).toBe(true);
  });

  it('should not allow concurrent runs', async () => {
    const testQueue = new TrackerQueue({ batchSize: 1, concurrency: 1, batchDelayMs: 1 });
    testQueue.setProcessFunction(() => Promise.resolve());
    await testQueue.store.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    await testQueue.run();
    expect(await testQueue.run()).toBe(false);
  });

  //TODO rename batchDelayMs to runDelayMs?
  it('should wait at least `batchDelayMs` between runs', async () => {
    jest.spyOn(global, 'setTimeout');
    const testQueue = new TrackerQueue({ batchSize: 1, concurrency: 1, batchDelayMs: 100 });
    testQueue.setProcessFunction(() => Promise.resolve());
    await testQueue.store.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(testQueue.running).toBe(false);
    await testQueue.run();
    expect(testQueue.running).toBe(false);
    expect(setTimeout).toHaveBeenCalledTimes(2);
  });
});
