/*
 * Copyright 2021 Objectiv B.V.
 */

import { ActionContext } from '@objectiv/schema';
import { makeActionContext as coreMakeActionContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable ActionContext.
 */
export const makeActionContext = (props: Parameters<typeof coreMakeActionContext>[0]): LocationContext<ActionContext> =>
  makeLocationContext<ActionContext>(coreMakeActionContext(props));
