/*
 * Copyright 2021 Objectiv B.V.
 */

/**
 * Converts the given text to a standardized format to be used as identifier for Location Contexts.
 * This may be used, among others, to infer a valid identifier from the title / label of a Button.
 */
export const makeIdFromString = (sourceString: string): string => {
  let id;

  if (typeof sourceString === 'string') {
    id = sourceString
      // Convert to lowercase
      .toLowerCase()
      // Trim it
      .trim()
      // Replace spaces with dashes
      .replace(/[\s]+/g, '-')
      // Remove non alphanumeric characters except dashes and underscores
      .replace(/[^a-zA-Z0-9_-]+/g, '')
      // Get rid of duplicated dashes
      .replace(/-+/g, '-')
      // Get rid of duplicated underscores
      .replace(/_+/g, '_')
      // Get rid of leading or trailing underscores and dashes
      .replace(/^([-_])*|([-_])*$/g, '')
      // Truncate to 64 chars
      .substr(0, 64);
  }

  // Throw if we did not manage to generate a valid id
  if (!id) {
    throw new Error('Could not generated a valid id. Please provide one manually.');
  }

  // Return processed id
  return id;
};
