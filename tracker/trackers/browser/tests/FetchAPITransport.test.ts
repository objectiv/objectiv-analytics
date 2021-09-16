import { QueuedTransport, TrackerEvent, TrackerQueue, TransportSendError } from '@objectiv/tracker-core';
import fetchMock from 'jest-fetch-mock';
import { defaultFetchFunction, defaultFetchParameters, FetchAPITransport } from '../src';

const MOCK_ENDPOINT = 'http://test-endpoint';

const testEvent = new TrackerEvent({
  _type: 'test-event',
});

describe('FetchAPITransport', () => {
  beforeAll(() => {
    fetchMock.enableMocks();
  });

  beforeEach(() => {
    fetchMock.resetMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should send using `fetch` API with the default fetch function', async () => {
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });
    await testTransport.handle(testEvent);
    const { id, ...otherProps } = testEvent;
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify({
          events: [
            {
              ...otherProps,
              id,
            },
          ],
          transport_time: Date.now(),
        }),
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
    const { id, ...otherProps } = testEvent;
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify({
          events: [
            {
              ...otherProps,
              id,
            },
          ],
          transport_time: Date.now(),
        }),
        ...customParameters,
      })
    );
  });

  it('should enqueue the event instead of sending it right away', async () => {
    jest.spyOn(global, 'setInterval');

    // Create a test queue
    const testQueue = new TrackerQueue();

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
    expect(testQueue.store.length).toBe(1);

    // Run timers to the next Queue tick.
    jest.advanceTimersByTime(testQueue.batchDelayMs);

    // Await for all promises to be fulfilled
    await new Promise(jest.requireActual('timers').setImmediate);

    // The Queue should have now sent the event by calling the runFunction once
    expect(setInterval).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(1);
    const { id, ...otherProps } = testEvent;
    expect(fetch).toHaveBeenCalledWith(
      MOCK_ENDPOINT,
      expect.objectContaining({
        body: JSON.stringify({
          events: [
            {
              ...otherProps,
              id,
            },
          ],
          transport_time: Date.now(),
        }),
        ...defaultFetchParameters,
      })
    );
  });

  it('should be safe to call with an empty array of Events for devs without TS', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });

    // @ts-ignore purposely disable TS and call the handle method anyway
    await testTransport.handle();

    // Fetch should not have been called
    expect(fetch).not.toHaveBeenCalled();
  });

  it('should reject with TransportSendError on http status !== 200', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });

    fetchMock.mockResponse('oops', { status: 500 });

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
  });

  it('should reject with TransportSendError on network failures', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchAPITransport({
      endpoint: MOCK_ENDPOINT,
    });

    fetchMock.mockReject();

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
  });
});
