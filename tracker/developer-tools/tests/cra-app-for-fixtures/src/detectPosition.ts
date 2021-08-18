import { mapStackFramesToSource, parseBrowserStackTrace } from '@objectiv/developer-tools';
import { TrackingAttribute, TrackedElementMetadata } from './tracker';

async function detectPosition(element: EventTarget) {
  const stackTrace = new Error().stack;
  const rawStackFrames = parseBrowserStackTrace(stackTrace);
  const mappedStackFrames = await mapStackFramesToSource(rawStackFrames);
  let elementMetadata: TrackedElementMetadata = {};

  if (element instanceof HTMLElement && element.getAttribute(TrackingAttribute.objectivElementId)) {
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
