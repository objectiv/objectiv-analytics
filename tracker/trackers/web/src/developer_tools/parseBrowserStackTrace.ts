/**
 * Prefixed in front of all console messages.
 */
const logPrefix = 'parseBrowserStackTrace';

/**
 * Stack traces are just multiline strings. Each line corresponds to a Stack Frame.
 */
type StackTraceString = string;

/**
 * Stack trace formats we support.
 */
enum StackTraceFormat {
  Chrome = 'Chrome',
  Firefox = 'Firefox',
}

/**
 * Regular expressions to detect Stack Trace format
 */
const StackTraceRegExp: { [key in StackTraceFormat]: RegExp } = {
  [StackTraceFormat.Chrome]: /\s*(at|in)\s.+(:\d+)/,
  [StackTraceFormat.Firefox]: /(|@)\S+:\d+|.+line\s+\d+\s+>\s+(eval|Function).+/,
};

/**
 * Regular expression to parse locationData from a Stack Trace line. Format is <file Name>:<lineNumber>:<columnNumber>
 */
const LocationRegExp = /\(?(.+?)(?::(\d+))?(?::(\d+))?\)?$/;

/**
 * Corresponds to one line of a Stack Trace and represents a function call.
 */
type StackFrame = {
  functionName: string;
  fileName: string;
  lineNumber: number;
  columnNumber: number;
};

/**
 * Attempts to parse a browser Error.stack by matching it against some regular expressions.
 * If a supported format is detected the stack trace string is converted to an array of StackFrame.
 */
export const parseBrowserStackTrace = (stackTrace?: StackTraceString): StackFrame[] => {
  // Nothing to do if we could not detect the Stack Trace format
  if (typeof stackTrace !== 'string' || !stackTrace.trim()) {
    console.log(`%c${logPrefix}: received empty Stack Trace`, 'font-weight:bold');
    return [];
  }

  // Attempt Stack Trace format detection (Chrome | Firefox)
  const stackTraceFormat = detectStackTraceFormat(stackTrace);

  // Nothing to do if we could not detect the Stack Trace format
  if (!stackTraceFormat) {
    console.groupCollapsed(`${logPrefix}: failed to detect Stack Trace format`);
    console.log(stackTrace);
    console.groupEnd();
    return [];
  }

  // Convert StackTrace to an array of Stack Frames
  return convertStackTraceToFrames(stackTrace, stackTraceFormat);
};

/**
 * Attempts to detect the given Stack Trace string is supported. Either Chrome or Firefox.
 * Returns null if we could not detect the format.
 */
const detectStackTraceFormat = (stackTrace: StackTraceString): StackTraceFormat | null => {
  // Test Chrome
  if (StackTraceRegExp.Chrome.test(stackTrace)) {
    return StackTraceFormat.Chrome;
  }

  // Test Firefox
  if (StackTraceRegExp.Firefox.test(stackTrace)) {
    return StackTraceFormat.Firefox;
  }

  return null;
};

/**
 * Converts a Stack Trace string to an array of Stack Frames
 */
const convertStackTraceToFrames = (stackTrace: StackTraceString, stackTraceFormat: StackTraceFormat): StackFrame[] => {
  // Convert Stack Trace string to a list of strings
  const stackTraceLines = stackTrace.split('\n');

  // Map each line to a Stack Frame
  switch (stackTraceFormat) {
    case StackTraceFormat.Chrome:
      return stackTraceLines.reduce<StackFrame[]>(chromeStackTraceLineToFrameReducer, []);
    case StackTraceFormat.Firefox:
      return stackTraceLines.reduce<StackFrame[]>(firefoxStackTraceLineToFrameReducer, []);
  }
};

/**
 * A reducer to convert a Chrome Stack Trace line to its Stack Frame representation.
 *
 * Automatically filters out lines that don't carry any Location (path:line:column) information. For example:
 *  - Error\n
 *  - Error: error message\n
 *  - at Array.map (<anonymous>)\n
 *  - at new Promise (<anonymous>)\n
 *
 */
const chromeStackTraceLineToFrameReducer = (stackFrames: StackFrame[], stackTraceLine: string): StackFrame[] => {
  // Skip this line if it doesn't match a useful Stack Frame, see documentation above for what that means
  if (!StackTraceRegExp.Chrome.test(stackTraceLine)) {
    return stackFrames;
  }

  // Stack Trace Lines with `eval` are sort-of nested. Throw away all `eval at ...` and keep only the innermost frame
  const evalFreeStackTraceLine = stackTraceLine.replace(/(\(eval at [^()]*)|(\),.*$)/g, '');

  // Trim and split by space(s)
  const linePieces = evalFreeStackTraceLine.trim().split(/\s+/g);

  // Slice away the first piece (`at `), reverse pieces, extract `locationData`. Store remaining pieces in `restOfLine`
  const [locationData, ...restOfLine] = linePieces.slice(1).reverse();

  // Join up `restOfLine` as `maybeFunctionName`. Default to `anonymous function` for lines without any function
  const maybeFunctionName = restOfLine.join(' ').trim();
  const functionName = maybeFunctionName !== '' ? maybeFunctionName : '<anonymous>';

  // Parse `locationData`
  const locationPieces =
    LocationRegExp.exec(locationData) ??
    // istanbul ignore next - This is dead code due to our regex test above. TS cannot detect it
    [];

  // Discard match and get `fileName`, `lineNumberString` and `columnNumberString` from the rest
  const [fileName, lineNumberString, columnNumberString] = locationPieces.slice(1);

  // Cast number strings to actual numbers
  const lineNumber = Number(lineNumberString);
  const columnNumber = Number(columnNumberString);

  return [
    ...stackFrames,
    {
      functionName,
      fileName,
      lineNumber,
      columnNumber,
    },
  ];
};

/**
 * A reducer to convert a Firefox Stack Trace line to its Stack Frame representation.
 *
 * Automatically filters out lines that don't carry any Location (path:line:column) information.
 * Haven't encountered any for FF, but we double check anyway for consistency.
 *
 */
const firefoxStackTraceLineToFrameReducer = (stackFrames: StackFrame[], stackTraceLine: string): StackFrame[] => {
  // Skip this line if it doesn't match a useful Stack Frame, see documentation above for what that means
  if (!StackTraceRegExp.Firefox.test(stackTraceLine)) {
    return stackFrames;
  }

  // Stack Trace Lines with `eval` prepend the location data with eval related information we don't need.
  const evalFreeStackTraceLine = stackTraceLine.replace(/line (\d+)(?: > eval line \d+)* > eval/g, '');

  // Trim and split by `@`
  const linePieces = evalFreeStackTraceLine.trim().split(/[@]/g);

  // Reverse pieces, extract `locationData`. Store remaining pieces in `restOfLine`
  const [locationData, ...restOfLine] = linePieces.reverse();

  // Join up `restOfLine` as `maybeFunctionName`. Default to `anonymous function` for lines without any function
  const maybeFunctionName = restOfLine.join(' ').trim();
  const functionName = maybeFunctionName !== '' ? maybeFunctionName : '<anonymous>';

  // Parse `locationData`
  const locationPieces =
    LocationRegExp.exec(locationData) ??
    // istanbul ignore next - This is dead code due to our regex test above. TS cannot detect it
    [];

  // Discard match and get `fileName`, `lineNumberString` and `columnNumberString` from the rest
  const [fileName, lineNumberString, columnNumberString] = locationPieces.slice(1);

  // Cast number strings to actual numbers
  const lineNumber = Number(lineNumberString);
  const columnNumber = Number(columnNumberString);

  return [
    ...stackFrames,
    {
      functionName,
      fileName,
      lineNumber,
      columnNumber,
    },
  ];
};
