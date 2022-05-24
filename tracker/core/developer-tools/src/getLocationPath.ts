/*
 * Copyright 2022 Objectiv B.V.
 */

import { LocationStack } from '@objectiv/tracker-core';

/**
 * Converts a Location Stack onto its human-readable Location Path
 */
export const getLocationPath = (locationStack: LocationStack) => {
  return locationStack.map((context) => `${context._type.replace('Context', '')}:${context.id}`).join(' / ');
};
