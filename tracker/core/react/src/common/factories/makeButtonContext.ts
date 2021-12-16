/*
 * Copyright 2021 Objectiv B.V.
 */

import { ButtonContext } from '@objectiv/schema';
import { makeButtonContext as coreMakeButtonContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable ButtonContext.
 */
export const makeButtonContext = (props: Parameters<typeof coreMakeButtonContext>[0]): LocationContext<ButtonContext> =>
  makeLocationContext<ButtonContext>(coreMakeButtonContext(props));
