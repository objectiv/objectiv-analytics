import { parseBrowserStackTrace } from '../src';

describe('parseBrowserStackTrace', () => {
  beforeEach(() => {
    spyOn(console, 'log');
    spyOn(console, 'groupCollapsed');
    spyOn(console, 'groupEnd');
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  it('should parse Chrome 90 stack trace as expected', () => {
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

    expect(stackFrames).toHaveLength(9);
    expect(stackFrames).toStrictEqual([
      {
        columnNumber: 1102,
        fileName: 'http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js',
        functionName: 'onClick',
        lineNumber: 1,
      },
      {
        columnNumber: 23594,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '$e',
        lineNumber: 2,
      },
      {
        columnNumber: 23748,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Ye',
        lineNumber: 2,
      },
      {
        columnNumber: 41955,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
      {
        columnNumber: 42049,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '_r',
        lineNumber: 2,
      },
      {
        columnNumber: 42464,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Cr',
        lineNumber: 2,
      },
      {
        columnNumber: 48117,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
      {
        columnNumber: 123976,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Fe',
        lineNumber: 2,
      },
      {
        columnNumber: 43925,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
    ]);
    expect(console.log).not.toHaveBeenCalled();
  });

  it('should parse Firefox 91 stack trace as expected', () => {
    const stackFrames = parseBrowserStackTrace(`
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

    expect(stackFrames).toHaveLength(16);
    expect(stackFrames).toStrictEqual([
      {
        columnNumber: 1102,
        fileName: 'http://0.0.0.0:5000/static/js/main.c56bb7a5.chunk.js',
        functionName: 'onClick',
        lineNumber: 1,
      },
      {
        columnNumber: 23594,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '$e',
        lineNumber: 2,
      },
      {
        columnNumber: 23748,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Ye',
        lineNumber: 2,
      },
      {
        columnNumber: 41955,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
      {
        columnNumber: 42049,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '_r',
        lineNumber: 2,
      },
      {
        columnNumber: 42466,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Cr',
        lineNumber: 2,
      },
      {
        columnNumber: 48119,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
      {
        columnNumber: 123976,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Fe',
        lineNumber: 2,
      },
      {
        columnNumber: 43927,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '<anonymous>',
        lineNumber: 2,
      },
      {
        columnNumber: 43955,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Or',
        lineNumber: 2,
      },
      {
        columnNumber: 32028,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Zt',
        lineNumber: 2,
      },
      {
        columnNumber: 31254,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Jt',
        lineNumber: 2,
      },
      {
        columnNumber: 129957,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 't.unstable_runWithPriority',
        lineNumber: 2,
      },
      {
        columnNumber: 52317,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: '$l',
        lineNumber: 2,
      },
      {
        columnNumber: 123715,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Me',
        lineNumber: 2,
      },
      {
        columnNumber: 31046,
        fileName: 'http://0.0.0.0:5000/static/js/2.2fd84a33.chunk.js',
        functionName: 'Xt',
        lineNumber: 2,
      },
    ]);
    expect(console.log).not.toHaveBeenCalled();
  });

  it('should return [] on empty or undefined stack traces and log the issue to console', () => {
    const testCaseStackTraces = [undefined, 0, 1, false, true, null, '', ' ', '\n', '\t', '\r', '\r\n', ' \n'];
    // @ts-ignore purposely ignore TypeScript warnings so we may pass wrong parameters to parseBrowserStackTrace
    const testCaseResults = testCaseStackTraces.map(parseBrowserStackTrace);

    testCaseResults.forEach((testCaseResult) => {
      expect(testCaseResult).toHaveLength(0);
    });

    expect(console.log).toHaveBeenCalledTimes(testCaseResults.length);

    testCaseResults.forEach((_, index) => {
      expect(console.log).toHaveBeenNthCalledWith(
        index + 1,
        `%cparseBrowserStackTrace: received empty Stack Trace`,
        'font-weight:bold'
      );
    });
  });

  it('should return [] on stack traces that cannot be recognized and log the issue to console', () => {
    // TODO add more cases
    const testCaseStackTraces = [`clearly not a stack trace`];
    const testCaseResults = testCaseStackTraces.map(parseBrowserStackTrace);

    testCaseResults.forEach((testCaseResult) => {
      expect(testCaseResult).toHaveLength(0);
    });

    expect(console.groupCollapsed).toHaveBeenCalledTimes(testCaseResults.length);
    expect(console.log).toHaveBeenCalledTimes(testCaseResults.length);
    expect(console.groupEnd).toHaveBeenCalledTimes(testCaseResults.length);

    testCaseResults.forEach((_, index) => {
      expect(console.groupCollapsed).toHaveBeenNthCalledWith(
        index + 1,
        `parseBrowserStackTrace: failed to detect Stack Trace format`
      );
      expect(console.log).toHaveBeenNthCalledWith(index + 1, testCaseStackTraces[index]);
    });
  });
});
