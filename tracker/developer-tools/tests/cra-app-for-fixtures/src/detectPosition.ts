import { mapStackFramesToSource, parseBrowserStackTrace } from '@objectiv/developer-tools';
import { DatasetAttribute, TrackerElementMetadata } from './tracker';

async function detectPosition(element: EventTarget) {
  const stackTrace = new Error().stack;
  const rawStackFrames = parseBrowserStackTrace(stackTrace);
  const mappedStackFrames = await mapStackFramesToSource(rawStackFrames);
  let elementMetadata: TrackerElementMetadata = {};

  if (element instanceof HTMLElement && element.getAttribute(DatasetAttribute.objectivElementId)) {
    elementMetadata = element.dataset;
  }

  return {
    stackTrace,
    rawStackFrames,
    mappedStackFrames,
    elementMetadata,
  };
}

export default detectPosition;
