/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { isTransportSendError, makeTransportSendError, TrackerEvent } from '@objectiv/tracker-core';
import fetchMock from 'jest-fetch-mock';
import { defaultFetchFunction, defaultFetchOptions, FetchTransport } from '../src';

const MOCK_ENDPOINT = 'http://test-endpoint';

const testEvent = new TrackerEvent({
  _type: 'test-event',
});

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('FetchTransport', () => {
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
    const testTransport = new FetchTransport({ endpoint: MOCK_ENDPOINT });
    expect(testTransport.isUsable()).toBe(true);
    await testTransport.handle(testEvent);
    expect(fetch).toHaveBeenCalledWith(MOCK_ENDPOINT, {
      body: JSON.stringify({
        events: [testEvent],
        transport_time: Date.now(),
      }),
      ...defaultFetchOptions,
    });
  });

  it('should send using `fetch` API with the provided customized fetch function', async () => {
    const customOptions: RequestInit = {
      ...defaultFetchOptions,
      mode: 'cors',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    const testTransport = new FetchTransport({
      endpoint: MOCK_ENDPOINT,
      fetchFunction: ({ endpoint, events }) => defaultFetchFunction({ endpoint, events, options: customOptions }),
    });
    await testTransport.handle(testEvent);
    expect(fetch).toHaveBeenCalledWith(MOCK_ENDPOINT, {
      body: JSON.stringify({
        events: [testEvent],
        transport_time: Date.now(),
      }),
      ...customOptions,
    });
  });

  it('should be safe to call with an empty array of Events for devs without TS', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchTransport({
      endpoint: MOCK_ENDPOINT,
    });

    // @ts-ignore purposely disable TS and call the handle method anyway
    await testTransport.handle();

    // Fetch should not have been called
    expect(fetch).not.toHaveBeenCalled();
  });

  it('should reject with TransportSendError on http status !== 200', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchTransport({ endpoint: MOCK_ENDPOINT });

    fetchMock.mockResponse('oops', { status: 500 });

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(isTransportSendError(error as Error)).toBe(true);
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(makeTransportSendError());
  });

  it('should reject with TransportSendError on network failures', async () => {
    // Create our Fetch Transport Instance
    const testTransport = new FetchTransport({
      endpoint: MOCK_ENDPOINT,
    });

    fetchMock.mockReject();

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(makeTransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(makeTransportSendError());
  });
});
