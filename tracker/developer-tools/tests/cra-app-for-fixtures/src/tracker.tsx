import { parseBrowserStackTrace } from '@objectiv/developer-tools';
import { v4 as uuidv4 } from 'uuid';

const TRACKING_DATASET_ATTRIBUTE_NAME = 'objectiv';
const TRACKING_FULL_ATTRIBUTE_NAME = `data-${TRACKING_DATASET_ATTRIBUTE_NAME}`;

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
  parentsMetadata: TrackerElementMetadata[];
};

export type TrackerElementTarget = EventTarget & {
  objectiv: string;
};

export const TrackerStore = new Map<string, TrackerElementMetadata>();

export const track = (contextId: string, contextType: ContextType, stackTrace: string = new Error().stack ?? '') => {
  const componentName = parseBrowserStackTrace(stackTrace)[2].functionName.replace(/\.render$/, '');
  const elementId = uuidv4();

  if (!TrackerStore.has(elementId)) {
    TrackerStore.set(elementId, { elementId, contextType, contextId, componentName, parentsMetadata: [] });
  }

  return {
    [TRACKING_FULL_ATTRIBUTE_NAME]: elementId,
  };
};

// FIXME this should go in its own module / context provider. Also it sucks :)
export const traverseAndCollectParentsMetadata = (
  htmlElement: HTMLElement | null,
  parentElements: TrackerElementMetadata[] = []
): TrackerElementMetadata[] => {
  if (!htmlElement) {
    return parentElements;
  }
  if (htmlElement.dataset.objectiv) {
    const trackerElementMetadata = TrackerStore.get(htmlElement.dataset.objectiv);
    if (trackerElementMetadata) {
      parentElements.push(trackerElementMetadata);
    }
  }
  return traverseAndCollectParentsMetadata(htmlElement.parentElement, parentElements);
};

const mutationObserver = new MutationObserver(() => {
  const trackedElementIds: string[] = [];
  const trackedElements = document.querySelectorAll('[data-objectiv]');
  trackedElements.forEach((trackedElement) => {
    if (trackedElement instanceof HTMLElement && trackedElement.dataset.objectiv) {
      const trackedElementId = trackedElement.dataset.objectiv;
      trackedElementIds.push(trackedElementId);
      const trackedElementMetadata = TrackerStore.get(trackedElementId);
      if (trackedElementMetadata) {
        TrackerStore.set(trackedElementId, {
          ...trackedElementMetadata,
          parentsMetadata: traverseAndCollectParentsMetadata(trackedElement).reverse(),
        });
      }
    }
  });
  // Cleanup store
  TrackerStore.forEach((trackedElementMetadata) => {
    if (!trackedElementIds.includes(trackedElementMetadata.elementId)) {
      TrackerStore.delete(trackedElementMetadata.elementId);
    }
  });
});

mutationObserver.observe(document, {
  attributeFilter: [TRACKING_FULL_ATTRIBUTE_NAME],
  attributeOldValue: true,
  subtree: true,
  childList: true,
});

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
