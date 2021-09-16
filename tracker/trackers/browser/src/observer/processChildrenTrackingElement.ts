import { getObjectKeys } from '@objectiv/tracker-core';
import { create } from 'superstruct';
import { parseChildrenAttribute, StringifiedTrackingAttributes, TrackChildrenQuery } from '../structs';
import { trackerErrorHandler } from '../tracker/trackerErrorHandler';
import { TrackingAttribute } from '../TrackingAttributes';
import { isChildrenTrackingElement, TrackedElement } from '../typeGuards';

/**
 * Check if Element is a Children Tracking Element. If so:
 * - Run its children tracking queries
 * - Decorate matching Elements intoTracked Elements
 * - Return a list of the decorated Elements
 */
const processChildrenTrackingElement = (element: Element): TrackedElement[] => {
  const newlyTrackedElements: TrackedElement[] = [];

  try {
    if (!isChildrenTrackingElement(element)) {
      return newlyTrackedElements;
    }
    const queries = parseChildrenAttribute(element.getAttribute(TrackingAttribute.trackChildren));

    queries.forEach((query: TrackChildrenQuery) => {
      const { queryAll, trackAs }: TrackChildrenQuery = create(query, TrackChildrenQuery);
      const trackingAsAttributes = create(trackAs, StringifiedTrackingAttributes);

      // Strip out undefined attributes
      getObjectKeys(trackingAsAttributes).forEach((key) => {
        if (trackingAsAttributes[key] === undefined) {
          delete trackingAsAttributes[key];
        }
      });

      element.querySelectorAll(queryAll).forEach((queriedElement) => {
        for (let [key, value] of Object.entries<string>(trackingAsAttributes)) {
          queriedElement.setAttribute(key, value);
        }

        newlyTrackedElements.push(queriedElement as TrackedElement);
      });
    });
  } catch (error) {
    trackerErrorHandler(error);
  }

  return newlyTrackedElements;
};

export default processChildrenTrackingElement;
