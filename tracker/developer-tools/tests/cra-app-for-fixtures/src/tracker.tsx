import { v4 as uuidv4 } from 'uuid';

export const DATASET_ATTRIBUTE_PREFIX = `data-objectiv`;
export const DATASET_ATTRIBUTE_ELEMENT_ID = `${DATASET_ATTRIBUTE_PREFIX}-element-id`;
export const DATASET_ATTRIBUTE_CONTEXT_TYPE = `${DATASET_ATTRIBUTE_PREFIX}-context-type`;
export const DATASET_ATTRIBUTE_CONTEXT_ID = `${DATASET_ATTRIBUTE_PREFIX}-context-id`;
export const DATASET_ATTRIBUTE_COMPONENT = `${DATASET_ATTRIBUTE_PREFIX}-component`;
export const DATASET_ATTRIBUTE_INTERACTIVE = `${DATASET_ATTRIBUTE_PREFIX}-interactive`;
export const DatasetAttribute = {
  objectivElementId: DATASET_ATTRIBUTE_ELEMENT_ID,
  objectivContextType: DATASET_ATTRIBUTE_CONTEXT_TYPE,
  objectivContextId: DATASET_ATTRIBUTE_CONTEXT_ID,
  objectivComponent: DATASET_ATTRIBUTE_COMPONENT,
  objectivInteractive: DATASET_ATTRIBUTE_INTERACTIVE,
};

// TODO get this from Schema._context_type literals
enum ContextType {
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

export const trackElement = (contextId: string, contextType: ContextType) => {
  const elementId = uuidv4();

  return {
    [DatasetAttribute.objectivElementId]: elementId,
    [DatasetAttribute.objectivContextType]: contextType,
    [DatasetAttribute.objectivContextId]: contextId,
  };
};

export const trackButton = (contextId: string) => trackElement(contextId, ContextType.button);

export const trackDiv = (contextId: string) => trackElement(contextId, ContextType.section);

export const trackHeader = (contextId: string) => trackElement(contextId, ContextType.section);

export const trackLink = (contextId: string) => trackElement(contextId, ContextType.link);

export const trackSpan = (contextId: string) => trackElement(contextId, ContextType.section);

const logClick = () => {
  console.log('should track this!');
}

function trackInteractiveElements(node: HTMLElement) {
  const elements = node.querySelectorAll(`[${DatasetAttribute.objectivElementId}]`);
  elements.forEach((element) => {
    if (element instanceof HTMLElement) {
      const isInteractive = element.getAttribute(DatasetAttribute.objectivInteractive) === 'true';
      if (isInteractive) {
        element.addEventListener('click', logClick, element.dataset)
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
