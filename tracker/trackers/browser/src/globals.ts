/**
 * Helper function to check if window exists. Used to detect non-browser environments.
 */
export const windowExists = () => typeof window !== 'undefined';

/**
 * Helper function to get the current Location href
 */
export const getLocationHref = () => {
  if (typeof location === 'undefined') {
    return undefined;
  }

  return location.href;
};
