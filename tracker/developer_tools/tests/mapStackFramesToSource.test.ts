import fetchMock from 'jest-fetch-mock';
import { mapStackFramesToSource } from "../src";
import { chrome_91, testScript } from './fixturesAndExpectations';

beforeEach(() => {
  fetchMock.mockIf(testScript.fileName, testScript.sourceCode);
  fetchMock.mockIf(testScript.sourceMappingURL, testScript.sourceMap);
});
afterEach(() => {
  fetchMock.resetMocks();
});

describe('mapStackFramesToSource', () => {
  it('should parse Chrome stack trace as expected', () => {
    mapStackFramesToSource(chrome_91.stackFrames);
  });
});
