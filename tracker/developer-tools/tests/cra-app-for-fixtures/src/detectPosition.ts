import { mapStackFramesToSource, parseBrowserStackTrace } from '@objectiv/developer-tools';
import { TrackerStore } from './tracker';

async function detectPosition(elementId: string) {
  const stackTrace = new Error().stack;
  const rawStackFrames = parseBrowserStackTrace(stackTrace);
  const mappedStackFrames = await mapStackFramesToSource(rawStackFrames);
  const elementMetadata = TrackerStore.get(elementId);

  return {
    stackTrace,
    rawStackFrames,
    mappedStackFrames,
    elementMetadata,
  };
}

export default detectPosition;
