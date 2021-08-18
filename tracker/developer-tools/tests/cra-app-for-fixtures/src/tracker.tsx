import { v4 as uuidv4 } from 'uuid';

export const TrackingAttribute = {
  objectivElementId: 'data-objectiv-element-id',
  objectivContextType: 'data-objectiv-context-type',
  objectivContextId: 'data-objectiv-context-id',
  objectivComponent: 'data-objectiv-component',
  objectivTrackClick: 'data-objectiv-track-click',
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

const makeTrackingAttributes = (contextType: string, contextId: string) => {
  const elementId = uuidv4();

  return {
    [TrackingAttribute.objectivElementId]: elementId,
    [TrackingAttribute.objectivContextType]: contextType,
    [TrackingAttribute.objectivContextId]: contextId
  }
}

type ContextInstance = {
  id: string;
  type: string;
};

type trackElementReturnType = ReturnType<typeof makeTrackingAttributes>

export function trackElement(contextId: string, contextType?: ContextType): trackElementReturnType;
export function trackElement(contextInstance: ContextInstance): trackElementReturnType;
export function trackElement(context: string | ContextInstance, contextType?: ContextType): trackElementReturnType {
  if (typeof context === 'string') {
    return makeTrackingAttributes(contextType ?? ContextType.section, context);
  } else {
    return makeTrackingAttributes(context.type, context.id);
  }
}

const track = (event: Event, element: HTMLElement) => {
  if (!(event.target instanceof HTMLElement)) {
    return;
  }

  const targetId = event.target.getAttribute(TrackingAttribute.objectivElementId);
  const elementId = element.getAttribute(TrackingAttribute.objectivElementId);
  if (targetId !== elementId) {
    return;
  }

  const metadata = traverseAndCollectParentsTrackingAttributes(element).reverse();

  const meta = element.dataset;
  console.log(
    `Tracking ${meta.objectivComponent} - Location Stack`,
    metadata.map((meta) => `${meta.objectivContextType}:${meta.objectivContextId}`)
  );
};

function trackInteractiveElements(node: HTMLElement) {
  const elements = node.querySelectorAll(`[${TrackingAttribute.objectivElementId}]`);
  elements.forEach((element) => {
    if (element instanceof HTMLElement) {
      const trackClick = element.dataset.objectivTrackClick === 'true';
      if (trackClick) {
        element.addEventListener('click', (event: Event) => track(event, element));
      }
    }
  });
}

const mutationObserver = new MutationObserver((mutationsList) => {
  mutationsList.forEach(({ addedNodes }) => {
    addedNodes.forEach((addedNode) => {
      if (addedNode instanceof HTMLElement) {
        trackInteractiveElements(addedNode);
      }
    });
  });
});

mutationObserver.observe(document, { childList: true, subtree: true });

export const traverseAndCollectParentsTrackingAttributes = (
  element?: Element | null,
  parentElements: TrackerElementMetadata[] = []
): TrackerElementMetadata[] => {
  if (!element) {
    return parentElements;
  }
  if (element instanceof HTMLElement && element.getAttribute(TrackingAttribute.objectivElementId)) {
    parentElements.push(element.dataset);
  }
  return traverseAndCollectParentsTrackingAttributes(element.parentElement, parentElements);
};
