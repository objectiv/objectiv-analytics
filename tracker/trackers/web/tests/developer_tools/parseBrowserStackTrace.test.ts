import { parseBrowserStackTrace } from '../../src/developer_tools';
import { chrome_91, firefox_90 } from './fixturesAndExpectations';

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

  it('should parse Chrome stack trace as expected', () => {
    const stackFrames = parseBrowserStackTrace(chrome_91.stackTrace);

    expect(stackFrames).toHaveLength(33);
    expect(stackFrames).toStrictEqual(chrome_91.stackFrames);
    expect(console.log).not.toHaveBeenCalled();
  });

  it('should parse Firefox stack trace as expected', () => {
    const stackFrames = parseBrowserStackTrace(firefox_90.stackTrace);

    expect(stackFrames).toHaveLength(42);
    // TODO
    // expect(stackFrames).toStrictEqual(firefox_90.stackFrames);
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
    const testCaseStackTraces = ['a'];
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
