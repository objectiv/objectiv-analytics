/*
 * Copyright 2021 Objectiv B.V.
 */

import { AbstractLocationContext } from '@objectiv/schema';
import { generateUUID } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';

/**
 * A utility to factor a new uniquely identifiable LocationContext.
 * To achieve so we add an extra attribute `__location_id` to the LocationContext factored with the core factory.
 */
export const makeLocationContext = <T extends AbstractLocationContext>(locationContext: T): LocationContext<T> => ({
  __location_id: generateUUID(),
  ...locationContext,
});
