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
  const stackFramesChrome = parseBrowserStackTrace(`
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

  const stackFramesFirefox = parseBrowserStackTrace(`
    @http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js line 1 > eval:1:28
    onClick@http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js:1:1102
    $e@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:23594
    Ye@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:23748
    _r/<@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:41955
    _r@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:42049
    Cr@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:42466
    Or/<@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:48119
    Fe@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:123976
    Or/<@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:43927
    Or@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:43955
    Zt@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:32028
    Jt@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:31254
    t.unstable_runWithPriority@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:129957
    $l@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:52317
    Me@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:123715
    Xt@http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js:2:31046
  `);

  const expectedMappedStackFrames = [
    {
      columnNumber: 31,
      fileName: 'App.tsx',
      functionName: 'onClick',
      lineNumber: 10,
      sourceCodePreview: [
        {
          isFrameTarget: false,
          line: '        <p>',
          lineNumber: 7,
        },
        {
          isFrameTarget: false,
          line: '          Edit <code>src/App.tsx</code> and save to reload.',
          lineNumber: 8,
        },
        {
          isFrameTarget: false,
          line: '        </p>',
          lineNumber: 9,
        },
        {
          isFrameTarget: true,
          line: "        <button onClick={() => eval('console.log(JSON.stringify(new Error().stack))')}>Trigger eval exception</button>",
          lineNumber: 10,
        },
        {
          isFrameTarget: false,
          line: '      </header>',
          lineNumber: 11,
        },
        {
          isFrameTarget: false,
          line: '    </div>',
          lineNumber: 12,
        },
        {
          isFrameTarget: false,
          line: '  );',
          lineNumber: 13,
        },
      ],
    },
  ];

  it('should map stack traces as expected', async () => {
    const mappedSTackFramesChrome = await mapStackFramesToSource(stackFramesChrome);
    const mappedSTackFramesFirefox = await mapStackFramesToSource(stackFramesFirefox);

    expect(mappedSTackFramesChrome).toStrictEqual(mappedSTackFramesFirefox);
    expect(mappedSTackFramesChrome).toStrictEqual(expectedMappedStackFrames);
    expect(mappedSTackFramesFirefox).toStrictEqual(expectedMappedStackFrames);
  });
});
