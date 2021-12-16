/*
 * Copyright 2021 Objectiv B.V.
 */

import { NavigationContext } from '@objectiv/schema';
import { makeNavigationContext as coreMakeNavigationContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable NavigationContext.
 */
export const makeNavigationContext = (
  props: Parameters<typeof coreMakeNavigationContext>[0]
): LocationContext<NavigationContext> => makeLocationContext<NavigationContext>(coreMakeNavigationContext(props));
