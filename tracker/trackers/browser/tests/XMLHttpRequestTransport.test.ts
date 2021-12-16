/*
 * Copyright 2021 Objectiv B.V.
 */

import { mockConsole } from '@objectiv/testing-tools';
import { TrackerEvent, TransportSendError } from '@objectiv/tracker-core';
import xhrMock from 'xhr-mock';
import { XMLHttpRequestTransport } from '../src';

beforeEach(() => {
  jest.spyOn(console, 'error').mockImplementation(() => {});
  xhrMock.setup();
  jest.useFakeTimers();
});

afterEach(() => {
  xhrMock.teardown();
  jest.useRealTimers();
  jest.resetAllMocks();
});

describe('XMLHttpRequestTransport', () => {
  const MOCK_ENDPOINT = '/test-endpoint';

  const testEvent = new TrackerEvent({
    _type: 'test-event',
  });

  it('should send using `xhr` with the default xhr function', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });
    const testTransportWithConsole = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
      console: mockConsole,
    });

    expect(testTransport.isUsable()).toBe(true);
    expect(testTransportWithConsole.isUsable()).toBe(true);

    xhrMock.post(MOCK_ENDPOINT, (req, res) => {
      expect(req.header('Content-Type')).toEqual('text/plain');
      expect(req.body()).toEqual(
        JSON.stringify({
          events: [testEvent],
          transport_time: Date.now(),
        })
      );
      return res.status(200);
    });

    await testTransport.handle(testEvent);
    await testTransportWithConsole.handle(testEvent);
  });

  it('should send using `xhr` with the default xhr function - 500 error example', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });
    const testTransportWithConsole = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
      console: mockConsole,
    });

    xhrMock.post(MOCK_ENDPOINT, {
      status: 500,
      reason: 'oops',
    });

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    try {
      await testTransportWithConsole.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
    await expect(testTransportWithConsole.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
  });

  it('should send using `xhr` with the default xhr function - onError example', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });
    const testTransportWithConsole = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
      console: mockConsole,
    });

    xhrMock.post(MOCK_ENDPOINT, () => Promise.reject());

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    try {
      await testTransportWithConsole.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(new TransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
    await expect(testTransportWithConsole.handle(testEvent)).rejects.toStrictEqual(new TransportSendError());
  });

  it('should send using `xhr` with the provided customized xhr function', async () => {
    const customXMLHttpRequestFunction = ({
      endpoint,
      events,
    }: {
      endpoint: string;
      events: TrackerEvent[];
    }): Promise<unknown> => {
      return new Promise(function (resolve, reject) {
        const xhr = new XMLHttpRequest();
        const async = true;
        xhr.open('POST', endpoint, async);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('Custom-Header-X', 'custom-header-value');
        xhr.withCredentials = false;
        xhr.onload = function () {
          if (this.status >= 200 && this.status < 300) {
            resolve(xhr.response);
          } else {
            reject({
              status: xhr.status,
              statusText: xhr.statusText,
            });
          }
        };
        xhr.onerror = function () {
          reject({
            status: xhr.status,
            statusText: xhr.statusText,
          });
        };
        xhr.send(JSON.stringify(events));
      });
    };

    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
      xmlHttpRequestFunction: customXMLHttpRequestFunction,
    });

    xhrMock.post(MOCK_ENDPOINT, (req, res) => {
      expect(req.header('Content-Type')).toEqual('application/json');
      expect(req.header('Custom-Header-X')).toEqual('custom-header-value');
      expect(req.body()).toEqual(JSON.stringify([testEvent]));
      return res.status(200);
    });

    await testTransport.handle(testEvent);
  });

  it('should be safe to call with an empty array of Events for devs without TS', async () => {
    // Create our XMLHttpRequest Transport Instance
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });
    jest.spyOn(testTransport, 'xmlHttpRequestFunction');

    // @ts-ignore purposely disable TS and call the handle method anyway
    await testTransport.handle();

    // XMLHttpRequest should not have been executed
    expect(testTransport.xmlHttpRequestFunction).not.toHaveBeenCalled();
  });
});
