/**
 * Corresponds to one line of a Stack Trace and represents a function call.
 */
export type StackFrame = {
  functionName: string;
  fileName: string;
  lineNumber: number;
  columnNumber: number;
  sourceCodePreview?: {
    lineNumber: number,
    line: string,
    isFrameTarget: boolean,
  }[]
};
