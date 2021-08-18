import { v4 as uuidv4 } from 'uuid';
// TODO Switch to superjson since it supports generics both when serializing and parsing
import serialize from 'serialize-javascript';

export const TrackingAttribute = {
  objectivElementId: 'data-objectiv-element-id',
  objectivContext: 'data-objectiv-context',
  objectivComponent: 'data-objectiv-component',
  objectivTrackClick: 'data-objectiv-track-click',
};

// TODO get this from Schema._context_type literals
export enum ContextType {
  section = 'SectionContext',
  button = 'ButtonContext',
  link = 'LinkContext',
}

export type TrackedElementMetadata = {
  objectivElementId?: string;
  objectivContext?: string;
  objectivComponent?: string;
};

type ContextInstance = {
  id: string;
  __context_type: string;
};

const makeTrackingAttributes = (contextType: string, contextId: string) => {
  const elementId = uuidv4();
  const serializedContext = serialize({ __context_type: contextType, id: contextId });

  return {
    [TrackingAttribute.objectivElementId]: elementId,
    [TrackingAttribute.objectivContext]: serializedContext
  }
}

type trackElementReturnType = ReturnType<typeof makeTrackingAttributes>

export function trackElement(contextId: string, contextType?: ContextType): trackElementReturnType;
export function trackElement(contextInstance: ContextInstance): trackElementReturnType;
export function trackElement(context: string | ContextInstance, contextType?: ContextType): trackElementReturnType {
  if (typeof context === 'string') {
    return makeTrackingAttributes(contextType ?? ContextType.section, context);
  } else {
    return makeTrackingAttributes(context.__context_type, context.id);
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
    metadata.map((meta) => {
      const contextInstance = meta.objectivContext ? JSON.parse(meta.objectivContext) : null;
      if (contextInstance) {
        return `${contextInstance.__context_type}:${contextInstance.id}`
      }
      return null;
    })
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
  parentElements: TrackedElementMetadata[] = []
): TrackedElementMetadata[] => {
  if (!element) {
    return parentElements;
  }
  // TODO write a type guard to determine if this is a complete tracked element, only the ID means nothing
  if (element instanceof HTMLElement && element.getAttribute(TrackingAttribute.objectivElementId)) {
    parentElements.push(element.dataset);
  }
  return traverseAndCollectParentsTrackingAttributes(element.parentElement, parentElements);
};
