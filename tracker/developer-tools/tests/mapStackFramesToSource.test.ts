import fetchMock from 'jest-fetch-mock';
import path from 'path';
import fs from 'fs';
import { mapStackFramesToSource, parseBrowserStackTrace } from '../src';

beforeAll(() => {
  fetchMock.enableMocks();
});

beforeEach(() => {
  fetchMock.mockIf(/^http:\/\/0.0.0.0:5000.*$/, (request: Request) => {
    // Replace remote url with local one
    const fixturePath = path.resolve(
      __dirname,
      request.url.replace('http://0.0.0.0:5000/', './cra-app-for-fixtures/build/')
    );


    console.log(`Mapping "${request.url}" to "${fixturePath}"`);

    return Promise.resolve(fs.readFileSync(fixturePath).toString());
  });
});
afterEach(() => {
  fetchMock.resetMocks();
});

describe('mapStackFramesToSource', () => {
  it('should parse Chrome stack trace as expected', async () => {
    const stackFrames = parseBrowserStackTrace(`
      Error
      at eval (eval at onClick (http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js:1:1102), <anonymous>:1:28)
      at onClick (http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js:1:1102)
      at Object.$e (http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:23594)
      at Ye (http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:23748)
      at http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:41955
      at _r (http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:42049)
      at Cr (http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:42464)
      at http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:48117
      at Fe (http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:123976)
      at http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:43925
    `);
    await mapStackFramesToSource(stackFrames);
  });
});
