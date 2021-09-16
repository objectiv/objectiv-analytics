import { TrackerEvent, TrackerQueue, TrackerQueueMemoryStore } from '../src';

beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

describe('TrackerQueueMemoryStore', () => {
  const TrackerEvent1 = new TrackerEvent({ _type: 'a' });
  const TrackerEvent2 = new TrackerEvent({ _type: 'b' });
  const TrackerEvent3 = new TrackerEvent({ _type: 'c' });

  it('should read all Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    const events = await trackerQueueStore.read();

    expect(events.map((event) => event._type)).toStrictEqual(['a', 'b', 'c']);
  });

  it('should allow filtering when reading Events', async () => {
    const trackerQueueStore = new TrackerQueueMemoryStore();
    await trackerQueueStore.write(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(trackerQueueStore.length).toBe(3);

    const events = await trackerQueueStore.read(Infinity, (event) => event._type !== 'a');

    expect(events.map((event) => event._type)).toStrictEqual(['b', 'c']);
  });
});

describe('TrackerQueue', () => {
  const TrackerEvent1 = new TrackerEvent({ _type: 'a' });
  const TrackerEvent2 = new TrackerEvent({ _type: 'b' });
  const TrackerEvent3 = new TrackerEvent({ _type: 'c' });

  it('should instantiate to a 0 length Queue', () => {
    const testQueue = new TrackerQueue();
    expect(testQueue.store.length).toBe(0);
  });

  it('should allow enqueuing multiple items at once', () => {
    const testQueue = new TrackerQueue();
    testQueue.push(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(testQueue.store.length).toBe(3);
  });

  it('should allow setting batchSize and batchDelayMs', () => {
    const testQueue = new TrackerQueue({ batchSize: 123, batchDelayMs: 456 });
    expect(testQueue.batchSize).toBe(123);
    expect(testQueue.batchDelayMs).toBe(456);
  });

  it('should throw an exception if the processFunction has not been set', async () => {
    const testQueue = new TrackerQueue({ batchSize: 1 });
    await expect(testQueue.run()).rejects.toBe('TrackerQueue `processFunction` has not been set.');
  });

  it('should enqueue and dequeue in the expected order', async () => {
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    const memoryStore = new TrackerQueueMemoryStore();
    const testQueue = new TrackerQueue({ batchSize: 1, concurrency: 1, store: memoryStore });
    testQueue.setProcessFunction(processFunctionSpy);
    expect(testQueue.store.length).toBe(0);

    await testQueue.push(TrackerEvent1);
    expect(memoryStore.length).toBe(1);

    await testQueue.push(TrackerEvent2);
    expect(memoryStore.length).toBe(2);

    await testQueue.push(TrackerEvent3);
    expect(memoryStore.length).toBe(3);

    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent1);
    expect(memoryStore.length).toBe(2);

    processFunctionSpy.mockClear();
    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent2);
    expect(memoryStore.length).toBe(1);

    processFunctionSpy.mockClear();
    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent3);
    expect(memoryStore.length).toBe(0);
  });

  it('should support batches', async () => {
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    const testQueue = new TrackerQueue({ batchSize: 2, concurrency: 1 });
    testQueue.setProcessFunction(processFunctionSpy);
    await testQueue.push(TrackerEvent1, TrackerEvent2, TrackerEvent3);
    expect(testQueue.store.length).toBe(3);

    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent1, TrackerEvent2);
    expect(testQueue.store.length).toBe(1);
    expect(testQueue.processingEventIds).toHaveLength(0);

    processFunctionSpy.mockClear();
    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledWith(TrackerEvent3);
    expect(testQueue.store.length).toBe(0);
    expect(testQueue.processingEventIds).toHaveLength(0);

    processFunctionSpy.mockClear();
    await testQueue.run();

    expect(processFunctionSpy).not.toHaveBeenCalled();
    expect(testQueue.store.length).toBe(0);
    expect(testQueue.processingEventIds).toHaveLength(0);
  });

  it('should support concurrent batches', async () => {
    const TrackerEvent4 = new TrackerEvent({ _type: 'd' });
    const TrackerEvent5 = new TrackerEvent({ _type: 'e' });
    const TrackerEvent6 = new TrackerEvent({ _type: 'f' });
    const TrackerEvent7 = new TrackerEvent({ _type: 'g' });
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    const testQueue = new TrackerQueue({ batchSize: 3, concurrency: 3 });
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
    expect(testQueue.store.length).toBe(7);

    await testQueue.run();

    expect(processFunctionSpy).toHaveBeenCalledTimes(3);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(1, ...[TrackerEvent1, TrackerEvent2, TrackerEvent3]);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(2, ...[TrackerEvent4, TrackerEvent5, TrackerEvent6]);
    expect(processFunctionSpy).toHaveBeenNthCalledWith(3, ...[TrackerEvent7]);
    expect(testQueue.store.length).toBe(0);
    expect(testQueue.processingEventIds).toHaveLength(0);
  });

  it('startRunner should start the setInterval that will execute `run` automatically after enough time', async () => {
    const processFunctionSpy = jest.fn(() => Promise.resolve());
    const testQueue = new TrackerQueue();
    testQueue.setProcessFunction(processFunctionSpy);

    jest.spyOn(testQueue, 'run');
    expect(testQueue.run).not.toHaveBeenCalled();

    testQueue.startRunner();

    jest.advanceTimersByTime(testQueue.batchDelayMs);

    expect(testQueue.run).toHaveBeenCalled();
  });
});
