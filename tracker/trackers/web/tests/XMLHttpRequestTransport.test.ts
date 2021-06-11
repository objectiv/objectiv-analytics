import { TrackerEvent } from '@objectiv/core';
import xhrMock from 'xhr-mock';
import { XMLHttpRequestTransport } from '../src';

beforeEach(() => {
  xhrMock.setup();
});

afterEach(() => {
  xhrMock.teardown();
});

describe('XMLHttpRequestTransport', () => {
  const MOCK_ENDPOINT = '/test-endpoint';

  const testEvent = new TrackerEvent({
    eventName: 'test-event',
  });

  it('should send using `xhr` with the default xhr function', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });

    expect(testTransport.isUsable()).toBe(true);

    xhrMock.post(MOCK_ENDPOINT, (req, res) => {
      expect(req.header('Content-Type')).toEqual('text/plain');
      expect(req.body()).toEqual(JSON.stringify([testEvent]));
      return res.status(200);
    });

    await testTransport.handle(testEvent);
  });

  it('should send using `xhr` with the default xhr function - 500 error example', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });

    xhrMock.post(MOCK_ENDPOINT, {
      status: 500,
      reason: 'oops',
    });

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual({ status: 500, statusText: 'oops' });
    }
  });

  it('should send using `xhr` with the default xhr function - onError example', async () => {
    const testTransport = new XMLHttpRequestTransport({
      endpoint: MOCK_ENDPOINT,
    });

    xhrMock.post(MOCK_ENDPOINT, () => Promise.reject());

    try {
      await testTransport.handle(testEvent);
    } catch (error) {
      expect(error).toStrictEqual({ status: 0, statusText: '' });
    }
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
});
