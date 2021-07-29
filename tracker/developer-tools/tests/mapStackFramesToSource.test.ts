import fetchMock from 'jest-fetch-mock';
import path from 'path';
import fs from 'fs';
import { mapStackFramesToSource, parseBrowserStackTrace } from '../src';
import craFixturesAppAssetManifest from './cra-app-for-fixtures/build/asset-manifest.json';

beforeAll(() => {
  fetchMock.enableMocks();
});

beforeEach(() => {
  fetchMock.mockIf(/^http:\/\/0.0.0.0:5000.*$/, (request: Request) => {
    const fixturePath = path
      // Replace remote url with local one
      .resolve(__dirname, request.url.replace('http://0.0.0.0:5000/', './cra-app-for-fixtures/build/'))
      // Get rid of hashcode and `.chunk` from the file name for `main` and `runtime` chunks.
      .replace(/.(main|runtime-main)..{8}.chunk.js$/, '/$1.js');

    const assetName = path.basename(fixturePath);
    let actualBuildFileToFetch = fixturePath;

    // For `main` and `runtime` we use the manifest of the built app to map the file we need to the actual file on disk
    if (['main.js', 'runtime-main.js'].includes(assetName)) {
      // @ts-ignore
      actualBuildFileToFetch = path.dirname(fixturePath) + craFixturesAppAssetManifest.files[assetName];
    }

    console.log(`Mapping "${request.url}" to "${actualBuildFileToFetch}"`);

    return Promise.resolve(fs.readFileSync(actualBuildFileToFetch).toString());
  });
});
afterEach(() => {
  fetchMock.resetMocks();
});

describe('mapStackFramesToSource', () => {
  it('should parse Chrome stack trace as expected', () => {
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
    mapStackFramesToSource(stackFrames);
  });
});
