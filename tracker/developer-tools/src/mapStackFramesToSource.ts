import { SourceMapConsumer } from 'source-map';
import { StackFrame } from './common';

/**
 * Given a source code string it parses the last `sourceMappingURL` entry from it.
 */
function getSourceMappingURLFromSourceCode(sourceCode: string): string | null {
  const sourceMappingURLRegex = /\/\/[#@] ?sourceMappingURL=([^\s'"]+)\s*$/gm;

  let sourceMappingUrl = null;
  let matchSourceMappingUrl;
  while ((matchSourceMappingUrl = sourceMappingURLRegex.exec(sourceCode))) {
    sourceMappingUrl = matchSourceMappingUrl[1];
  }

  return sourceMappingUrl;
}

/**
 * Retrieves the sourceMappingURL from the given sourceCode and determines if it's an actual URL or an inline base64
 * encoded Source Map. Then either decodes the sourceMap or fetches it as JSON Object and uses it to initialize and
 * return a SourceMapConsumer.
 */
const getSourceMapConsumer = async (fileName: string, sourceCode: string) => {
  // Attempt to retrieve the sourceMappingURL from the given sourceCode
  const sourceMappingURL = getSourceMappingURLFromSourceCode(sourceCode);
  if (!sourceMappingURL) {
    return Promise.reject(`Could not retrieve sourceMappingURL for ${fileName}`);
  }

  // Determine the kind of sourceMappingURL we got: inline or file
  const isInlineSourceMap = sourceMappingURL.startsWith('data:');

  let rawSourceMap;
  if (isInlineSourceMap) {
    const isBase64InlineSourceMapRegExp = /^data:application\/json;([\w=:"-]+;)*base64,/;
    const base64InlineSourceMapMatchArray = sourceMappingURL.match(isBase64InlineSourceMapRegExp);

    // Inline Source Maps must be base64 encoded
    if (base64InlineSourceMapMatchArray === null) {
      return Promise.reject('Inline source maps must be base64 encoded.');
    }

    // Get the encoded sourcemap from the URL itself
    const encodedInlineSourceMap = sourceMappingURL.substring(base64InlineSourceMapMatchArray.length);

    // Decode from base64 to string and parse to JSON Object
    const decodedInlineSourceMap = window.atob(encodedInlineSourceMap);
    rawSourceMap = JSON.parse(decodedInlineSourceMap);
  } else {
    // sourceMappingURL is relative to the fileName. Here we prepend sourceMappingURL with the same path of fileName.
    const index = fileName.lastIndexOf('/');
    const url = fileName.substring(0, index + 1) + sourceMappingURL;

    // Fetch the source map contents as JSON Object
    rawSourceMap = await fetch(url).then((res) => res.json());
  }

  // Create a new SourceMapConsumer either with the inline or the fetched SourceMap Object
  return new SourceMapConsumer(rawSourceMap);
};

/**
 * Attempts to parse a browser Error.stack by matching it against some regular expressions.
 * If a supported format is detected the stack trace string is converted to an array of StackFrame.
 */
export const mapStackFramesToSource = async (stackFrames: StackFrame[]): Promise<StackFrame[]> => {
  const sourceCache = new Map<string, { sourceCode: string; sourceMapConsumer: SourceMapConsumer }>();

  // Gather all fileNames
  const allFileNames = stackFrames.map(({ fileName }) => fileName);

  // Remove duplicates
  const fileNames = allFileNames.filter((fileName, index, allFileNames) => allFileNames.indexOf(fileName) === index);

  // For each fileName, fetch both its `sourceCode` and `sourceMapConsumer` and store them in `sourceCache`
  await Promise.all(
    fileNames.map(async (fileName) => {
      const sourceCode = await fetch(fileName).then((response) => response.text());
      const sourceMapConsumer = await getSourceMapConsumer(fileName, sourceCode);
      sourceCache.set(fileName, { sourceCode, sourceMapConsumer });
    })
  );

  // Now that we, hopefully, have SourceMapConsumers for all Stack Frame fileNames we can attempt to process them up
  const mappedStackFrames = stackFrames.map((stackFrame) => {
    const sourceCacheEntry = sourceCache.get(stackFrame.fileName);

    // If we can't find this stackFrame's fileName in our cache, just return the frame as-is
    if (!sourceCacheEntry) {
      console.log('No source cache entry found for stackFrame');
      return stackFrame;
    }

    // Retrieve the original position from the Source Map Consumer
    const originalPosition = sourceCacheEntry.sourceMapConsumer.originalPositionFor({
      line: stackFrame.lineNumber,
      column: stackFrame.columnNumber,
    });

    // TODO here we could extract the original source code from around this stack frame. Nice for logging or UI
    // Retrieve the original source code from the Source Map Consumer
    // const originalSourceCode = sourceCacheEntry.sourceMapConsumer.sourceContentFor(stackFrame.fileName)

    // Return a new StackFrame with the new values
    return {
      functionName: stackFrame.functionName,
      fileName: originalPosition.source,
      lineNumber: originalPosition.line,
      columnNumber: originalPosition.column,
    };
  });

  // Clean up `node_modules` frames and return the list of mapped stack frames
  return mappedStackFrames.filter((mappedStackFrame) => mappedStackFrame.fileName.indexOf('node_modules') < 0);
};
