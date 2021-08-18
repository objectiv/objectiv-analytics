import { v4 as uuidv4 } from 'uuid';

export const DATASET_ATTRIBUTE_PREFIX = `data-objectiv`;
export const DATASET_ATTRIBUTE_ELEMENT_ID = `${DATASET_ATTRIBUTE_PREFIX}-element-id`;
export const DATASET_ATTRIBUTE_CONTEXT_TYPE = `${DATASET_ATTRIBUTE_PREFIX}-context-type`;
export const DATASET_ATTRIBUTE_CONTEXT_ID = `${DATASET_ATTRIBUTE_PREFIX}-context-id`;
export const DATASET_ATTRIBUTE_COMPONENT = `${DATASET_ATTRIBUTE_PREFIX}-component`;
export const DATASET_ATTRIBUTE_TRACK_CLICK = `${DATASET_ATTRIBUTE_PREFIX}-track-click`;
export const DatasetAttribute = {
  objectivElementId: DATASET_ATTRIBUTE_ELEMENT_ID,
  objectivContextType: DATASET_ATTRIBUTE_CONTEXT_TYPE,
  objectivContextId: DATASET_ATTRIBUTE_CONTEXT_ID,
  objectivComponent: DATASET_ATTRIBUTE_COMPONENT,
  objectivTrackClick: DATASET_ATTRIBUTE_TRACK_CLICK,
};

// TODO get this from Schema._context_type literals
export enum ContextType {
  section = 'SectionContext',
  button = 'ButtonContext',
  link = 'LinkContext',
}

export type TrackerElementMetadata = {
  objectivElementId?: string;
  objectivContextType?: ContextType;
  objectivContextId?: string;
  objectivComponent?: string;
};

export type TrackerElementTarget = EventTarget & {
  objectiv: string;
};

export const trackElement = (contextId: string, contextType: ContextType = ContextType.section) => {
  const elementId = uuidv4();

  return {
    [DatasetAttribute.objectivElementId]: elementId,
    [DatasetAttribute.objectivContextType]: contextType,
    [DatasetAttribute.objectivContextId]: contextId,
  };
};

const track = (event: Event, element: HTMLElement) => {
  if (!(event.target instanceof HTMLElement)) {
    return;
  }

  const targetId = event.target.getAttribute(DatasetAttribute.objectivElementId);
  const elementId = element.getAttribute(DatasetAttribute.objectivElementId);
  if(targetId !== elementId) {
    return;
  }

  const metadata = traverseAndCollectParentsMetadata(element).reverse();

  const meta = element.dataset;
  console.log(`Tracking ${meta.objectivComponent} - Location Stack`, metadata.map(meta => `${meta.objectivContextType}:${meta.objectivContextId}`));
}

function trackInteractiveElements(node: HTMLElement) {
  const elements = node.querySelectorAll(`[${DatasetAttribute.objectivElementId}]`);
  elements.forEach((element) => {
    if (element instanceof HTMLElement) {
      const trackClick = element.getAttribute(DatasetAttribute.objectivTrackClick) === 'true';
      if (trackClick) {
        element.addEventListener('click', (event: Event) => track(event, element), element.dataset)
      }
    }
  });
}

const mutationObserver = new MutationObserver((mutationsList) => {
  mutationsList.forEach(({ addedNodes }) => {
    addedNodes.forEach(addedNode => {
      if (addedNode instanceof HTMLElement) {
        trackInteractiveElements(addedNode)
      }
    })
  })
});

mutationObserver.observe(document, { childList: true, subtree: true });

export const traverseAndCollectParentsMetadata = (
  element?: Element | null,
  parentElements: TrackerElementMetadata[] = []
): TrackerElementMetadata[] => {
  if (!element) {
    return parentElements;
  }
  if (element instanceof HTMLElement && element.getAttribute(DatasetAttribute.objectivElementId)) {
    parentElements.push(element.dataset);
  }
  return traverseAndCollectParentsMetadata(element.parentElement, parentElements);
};
