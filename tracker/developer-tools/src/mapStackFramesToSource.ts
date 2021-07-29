import { SourceMapConsumer } from 'source-map';
import { StackFrame } from './common';

function getSourceMappingURLFromSourceCode(sourceCode: string): string | null {
  const sourceMappingURLRegex = /\/\/[#@] ?sourceMappingURL=([^\s'"]+)\s*$/gm;

  let sourceMappingUrl = null;
  let matchSourceMappingUrl;
  while ((matchSourceMappingUrl = sourceMappingURLRegex.exec(sourceCode))) {
    sourceMappingUrl = matchSourceMappingUrl[1];
  }

  return sourceMappingUrl;
}

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

    // ???
    if (base64InlineSourceMapMatchArray === null) {
      throw new Error('Inline source maps must be base64 encoded.');
    }

    // ???
    const encodedInlineSourceMap = sourceMappingURL.substring(base64InlineSourceMapMatchArray.length);

    // ???
    const decodedInlineSourceMap = window.atob(encodedInlineSourceMap);

    // ???
    rawSourceMap = JSON.parse(decodedInlineSourceMap);
  } else {
    // Regular sourceMap
    const index = fileName.lastIndexOf('/');

    // ???
    const url = fileName.substring(0, index + 1) + sourceMappingURL;

    // ???
    rawSourceMap = await fetch(url).then((res) => res.json());
  }

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
  await fileNames.map(async (fileName) => {
    const sourceCode = await fetch(fileName).then((response) => response.text());
    const sourceMapConsumer = await getSourceMapConsumer(fileName, sourceCode);
    sourceCache.set(fileName, { sourceCode, sourceMapConsumer });
  });

  console.log(sourceCache);

  // return frames.map(frame => {
  //   const { functionName, fileName, lineNumber, columnNumber } = frame;
  //   let { map, fileSource } = cache[fileName] || {};
  //   if (map == null || lineNumber == null) {
  //     return frame;
  //   }
  //   const { source, line, column } = map.getOriginalPosition(
  //     lineNumber,
  //     columnNumber
  //   );
  //   const originalSource = source == null ? [] : map.getSource(source);
  //   return new StackFrame(
  //     functionName,
  //     fileName,
  //     lineNumber,
  //     columnNumber,
  //     getLinesAround(lineNumber, contextLines, fileSource),
  //     functionName,
  //     source,
  //     line,
  //     column,
  //     getLinesAround(line, contextLines, originalSource)
  //   );

  // TODO actual processing of the sourceMap
  return stackFrames;
};

// function getLinesAround(
//   line,
//   count,
//   lines
// ) {
//   if (typeof lines === 'string') {
//     lines = lines.split('\n');
//   }
//   const result = [];
//   for (
//     let index = Math.max(0, line - 1 - count);
//     index <= Math.min(lines.length - 1, line - 1 + count);
//     ++index
//   ) {
//     result.push(new ScriptLine(index + 1, lines[index], index === line - 1));
//   }
//   return result;
// }
