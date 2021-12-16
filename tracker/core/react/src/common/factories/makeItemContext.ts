/*
 * Copyright 2021 Objectiv B.V.
 */

import { ItemContext } from '@objectiv/schema';
import { makeItemContext as coreMakeItemContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable ItemContext.
 */
export const makeItemContext = (props: Parameters<typeof coreMakeItemContext>[0]): LocationContext<ItemContext> =>
  makeLocationContext<ItemContext>(coreMakeItemContext(props));
