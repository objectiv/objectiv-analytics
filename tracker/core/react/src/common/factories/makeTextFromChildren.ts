/*
 * Copyright 2021 Objectiv B.V.
 */

import { ReactNode } from 'react';
import { recursiveGetTextFromChildrenNode } from './recursiveGetTextFromChildren';

/**
 * Retrieve text from given ReactNode children.
 * The resulting text may be may be used, among others, to infer a valid text and identifier for a Button.
 *
 * @see makeIdFromString
 */
export const makeTextFromChildren = (children: ReactNode): string => {
  const text = recursiveGetTextFromChildrenNode(children);

  // Throw if we did not manage to get any text
  if (!text) {
    throw new Error('Could not infer any text from children nodes. Please provide one manually.');
  }

  return text.trim();
};
