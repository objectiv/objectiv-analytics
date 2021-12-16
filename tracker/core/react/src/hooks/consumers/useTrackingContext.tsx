/*
 * Copyright 2021 Objectiv B.V.
 */

import { TrackingContext } from '../../common/providers/TrackingContext';
import { useLocationStack } from './useLocationStack';
import { useTracker } from './useTracker';

/**
 * A utility hook to easily retrieve TrackingContext: tracker and locationStack.
 */
export const useTrackingContext = (): TrackingContext => {
  const tracker = useTracker();
  const locationStack = useLocationStack();

  return {
    tracker,
    locationStack,
  };
};
