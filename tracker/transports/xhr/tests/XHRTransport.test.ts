/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { makeTransportSendError, TrackerEvent } from '@objectiv/tracker-core';
import xhrMock from 'xhr-mock';
import { XHRTransport } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

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

describe('XHRTransport', () => {
  const MOCK_ENDPOINT = '/test-endpoint';

  const testEvent = new TrackerEvent({
    _type: 'test-event',
  });

  it('should send using `xhr` with the default xhr function', async () => {
    const testTransport = new XHRTransport({
      endpoint: MOCK_ENDPOINT,
    });

    expect(testTransport.isUsable()).toBe(true);

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
  });

  it('should send using `xhr` with the default xhr function - 500 error example', async () => {
    const testTransport = new XHRTransport({
      endpoint: MOCK_ENDPOINT,
    });

    xhrMock.post(MOCK_ENDPOINT, {
      status: 500,
      reason: 'oops',
    });

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(makeTransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(makeTransportSendError());
  });

  it('should send using `xhr` with the default xhr function - onError example', async () => {
    const testTransport = new XHRTransport({
      endpoint: MOCK_ENDPOINT,
    });

    xhrMock.post(MOCK_ENDPOINT, () => Promise.reject());

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual(makeTransportSendError());
    }

    await expect(testTransport.handle(testEvent)).rejects.toStrictEqual(makeTransportSendError());
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

    const testTransport = new XHRTransport({
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
    const testTransport = new XHRTransport({
      endpoint: MOCK_ENDPOINT,
    });
    jest.spyOn(testTransport, 'xmlHttpRequestFunction');

    // @ts-ignore purposely disable TS and call the handle method anyway
    await testTransport.handle();

    // XMLHttpRequest should not have been executed
    expect(testTransport.xmlHttpRequestFunction).not.toHaveBeenCalled();
  });
});
