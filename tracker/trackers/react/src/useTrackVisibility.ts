import { makeSectionHiddenEvent, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { ReactTracker } from './ReactTracker';
import { useTracker } from './TrackerContextProvider';
import { useTrackOnMount } from './useTrackOnMount';
import { useTrackOnUnmount } from './useTrackOnUnmount';

/**
 * A side effect that triggers SectionVisibleEvent and SectionHiddenEvent as the component mounts and unmounts.
 */
export const useTrackVisibility = (tracker: ReactTracker = useTracker()) => {
  useTrackOnMount(makeSectionVisibleEvent(), tracker);
  useTrackOnUnmount(makeSectionHiddenEvent(), tracker);
};
