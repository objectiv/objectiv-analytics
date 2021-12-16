/*
 * Copyright 2021 Objectiv B.V.
 */

import { InputContext } from '@objectiv/schema';
import { makeInputContext as coreMakeInputContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable InputContext.
 */
export const makeInputContext = (props: Parameters<typeof coreMakeInputContext>[0]): LocationContext<InputContext> =>
  makeLocationContext<InputContext>(coreMakeInputContext(props));
