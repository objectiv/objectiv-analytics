import { getLocationHref } from '../helpers';

/**
 * Global state
 */
export const AutoTrackingState: {
  observerInstance: MutationObserver | null;
  applicationLoaded: boolean;
  previousURL: string | undefined;
} = {
  /**
   * Holds the instance to the Tagged Elements Mutation Observer created by `startAutoTracking`
   */
  observerInstance: null,

  /**
   * Whether we already tracked the ApplicationLoaded Event or not
   */
  applicationLoaded: false,

  /**
   * Holds the last seen URL
   */
  previousURL: getLocationHref(),
};
