import fetchMock from 'jest-fetch-mock';
import { mapStackFramesToSource, parseBrowserStackTrace } from '../src';

beforeAll(() => {
  fetchMock.enableMocks();
});

beforeEach(() => {
  fetchMock.mockIf(/^http:\/\/localhost:3000.*$/, (request: Request) => {
    const fixtureURL = request.url.replace('http://localhost:3000/', './cra-app-for-fixtures/build/');
    console.log(`Mapping "${request.url}" to "${fixtureURL}"`);
    return fetch(fixtureURL).then((response) =>
      response.text()
    )
  });
});
afterEach(() => {
  fetchMock.resetMocks();
});

describe('mapStackFramesToSource', () => {
  it('should parse Chrome stack trace as expected', () => {
    const stackFrames = parseBrowserStackTrace(`Error
      at eval (eval at <anonymous> (eval at onClick (http://localhost:3000/static/js/main.chunk.js:41:24)), <anonymous>:1:1)
      at eval (eval at onClick (http://localhost:3000/static/js/main.chunk.js:41:24), <anonymous>:1:1)
      at onClick (http://localhost:3000/static/js/main.chunk.js:41:24)
      at HTMLUnknownElement.callCallback (http://localhost:3000/static/js/vendors~main.chunk.js:14571:18)
      at Object.invokeGuardedCallbackDev (http://localhost:3000/static/js/vendors~main.chunk.js:14620:20)
      at invokeGuardedCallback (http://localhost:3000/static/js/vendors~main.chunk.js:14680:35)
      at invokeGuardedCallbackAndCatchFirstError (http://localhost:3000/static/js/vendors~main.chunk.js:14695:29)
      at executeDispatch (http://localhost:3000/static/js/vendors~main.chunk.js:18930:7)
      at processDispatchQueueItemsInOrder (http://localhost:3000/static/js/vendors~main.chunk.js:18962:11)
      at processDispatchQueue (http://localhost:3000/static/js/vendors~main.chunk.js:18975:9)
      at dispatchEventsForPlugins (http://localhost:3000/static/js/vendors~main.chunk.js:18986:7)
      at http://localhost:3000/static/js/vendors~main.chunk.js:19197:16
      at batchedEventUpdates$1 (http://localhost:3000/static/js/vendors~main.chunk.js:32882:16)
      at batchedEventUpdates (http://localhost:3000/static/js/vendors~main.chunk.js:14369:16)
      at dispatchEventForPluginEventSystem (http://localhost:3000/static/js/vendors~main.chunk.js:19196:7)
      at attemptToDispatchEvent (http://localhost:3000/static/js/vendors~main.chunk.js:16679:7)
      at dispatchEvent (http://localhost:3000/static/js/vendors~main.chunk.js:16597:23)
      at unstable_runWithPriority (http://localhost:3000/static/js/vendors~main.chunk.js:9400:16)
      at runWithPriority$1 (http://localhost:3000/static/js/vendors~main.chunk.js:21977:14)
      at discreteUpdates$1 (http://localhost:3000/static/js/vendors~main.chunk.js:32899:18)
      at discreteUpdates (http://localhost:3000/static/js/vendors~main.chunk.js:14381:16)
      at dispatchDiscreteEvent (http://localhost:3000/static/js/vendors~main.chunk.js:16563:7)
    `);
    mapStackFramesToSource(stackFrames);
  });
});
