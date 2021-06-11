import fetchMock from 'jest-fetch-mock';
import { defaultFetchFunction, defaultFetchParameters, FetchAPITransport } from '../src';
import { MemoryQueue, QueuedTransport, TrackerEvent } from '@objectiv/tracker-core';

beforeAll(() => {
  fetchMock.enableMocks();
});

beforeEach(() => {
  fetchMock.resetMocks();
});

describe('FetchAPITransport', () => {
  const MOCK_ENDPOINT = '/test-endpoint';

  const testEvent = new TrackerEvent({
    event: 'test-event',
  });

  it('should send using `fetch` API with the default fetch function', async () => {
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });
    await testTransport.handle(testEvent);
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify([testEvent]),
        ...defaultFetchParameters,
      })
    );
  });

  it('should send using `fetch` API with the provided customized fetch function', async () => {
    const customParameters: RequestInit = {
      ...defaultFetchParameters,
      mode: 'cors',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
      fetchFunction: ({ endpoint, events }) => defaultFetchFunction({ endpoint, events, parameters: customParameters }),
    });
    await testTransport.handle(testEvent);
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify([testEvent]),
        ...customParameters,
      })
    );
  });

  it('should enqueue the event instead of sending it right away', async () => {
    jest.useFakeTimers();

    // Create a test queue
    const testQueue = new MemoryQueue();

    // Create our Fetch Transport Instance
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });

    // Combine the two in a Queued Transport
    const testQueuedTransport = new QueuedTransport({
      queue: testQueue,
      transport: testTransport,
    });

    // Let's handle an Event
    await testQueuedTransport.handle(testEvent);

    // Since we configured a Queue, the transport should not have called Fetch yet
    expect(fetch).not.toHaveBeenCalled();

    // Instead, it should have enqueued the TrackerEvent
    expect(testQueue.events).toContain(testEvent);

    // Run timers to the next Queue tick.
    jest.runTimersToTime(testQueue.batchDelayMs);

    // Await for all promises to be fulfilled
    await new Promise(setImmediate);

    // The Queue should have now sent the event by calling the runFunction once
    expect(setInterval).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify([testEvent]),
        ...defaultFetchParameters,
      })
    );
  });
});
