/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isTagChildrenElement } from '../common/guards/isTagChildrenElement';
import { parseTagChildren } from '../common/parsers/parseTagChildren';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggedElement } from '../definitions/TaggedElement';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { ValidChildrenTaggingQuery } from '../definitions/ValidChildrenTaggingQuery';

/**
 * Check if Element is a ChildrenTaggingElement. If so:
 * - Run its children tracking queries
 * - Decorate matching Elements into TaggedElements
 * - Return a list of the decorated Elements
 */
export const processTagChildrenElement = (element: Element): TaggedElement[] => {
  const newlyTrackedElements: TaggedElement[] = [];

  try {
    if (!isTagChildrenElement(element)) {
      return newlyTrackedElements;
    }
    const queries = parseTagChildren(element.getAttribute(TaggingAttribute.tagChildren));

    queries.forEach((query: ValidChildrenTaggingQuery) => {
      const { queryAll, tagAs }: ValidChildrenTaggingQuery = query;

      element.querySelectorAll(queryAll).forEach((queriedElement) => {
        for (let [key, value] of Object.entries<string | undefined>(tagAs)) {
          if (value) {
            queriedElement.setAttribute(key, value);
          }
        }

        newlyTrackedElements.push(queriedElement as TaggedElement);
      });
    });
  } catch (error) {
    trackerErrorHandler(error);
  }

  return newlyTrackedElements;
};
