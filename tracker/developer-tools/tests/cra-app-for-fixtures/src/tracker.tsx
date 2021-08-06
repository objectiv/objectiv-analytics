import { parseBrowserStackTrace } from '@objectiv/developer-tools';
import { v4 as uuidv4 } from 'uuid';

// TODO get this from Schema._context_type literals
enum ContextType {
  section = 'SectionContext',
  button = 'ButtonContext',
  link = 'LinkContext',
}

export type TrackerElementMetadata = {
  elementId: string;
  contextType: ContextType;
  contextId: string;
  componentName: string;
};

export type TrackerElementTarget = EventTarget & {
  objectiv: string;
};

export const TrackerStore = new Map<string, TrackerElementMetadata>();

// TODO memoize the whole thing?
export const track = (contextId: string, contextType: ContextType, stackTrace: string = new Error().stack ?? '') => {
  // TODO memoize across re-renders
  const componentName = parseBrowserStackTrace(stackTrace)[2].functionName;
  // TODO memoize across re-renders
  const elementId = uuidv4();

  if (!TrackerStore.has(elementId)) {
    TrackerStore.set(elementId, { elementId, contextType, contextId, componentName });
    console.log(`Tracking Element ${elementId}: ${contextType} with id '${contextId}' in ${componentName} component`);
  }

  return {
    'data-objectiv': elementId,
  };
};

export const trackButton = (contextId: string, stackTrace: string = new Error().stack ?? '') =>
  track(contextId, ContextType.button, stackTrace);

export const trackDiv = (contextId: string, stackTrace: string = new Error().stack ?? '') =>
  track(contextId, ContextType.section, stackTrace);

export const trackHeader = (contextId: string, stackTrace: string = new Error().stack ?? '') =>
  track(contextId, ContextType.section, stackTrace);

export const trackLink = (contextId: string, stackTrace: string = new Error().stack ?? '') =>
  track(contextId, ContextType.link, stackTrace);

export const trackSpan = (contextId: string, stackTrace: string = new Error().stack ?? '') =>
  track(contextId, ContextType.section, stackTrace);
