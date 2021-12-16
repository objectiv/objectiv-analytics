/*
 * Copyright 2021 Objectiv B.V.
 */

import { OverlayContext } from '@objectiv/schema';
import { makeOverlayContext as coreMakeOverlayContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable OverlayContext.
 */
export const makeOverlayContext = (
  props: Parameters<typeof coreMakeOverlayContext>[0]
): LocationContext<OverlayContext> => makeLocationContext<OverlayContext>(coreMakeOverlayContext(props));
