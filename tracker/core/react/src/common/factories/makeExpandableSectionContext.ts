/*
 * Copyright 2021 Objectiv B.V.
 */

import { ExpandableSectionContext } from '@objectiv/schema';
import { makeExpandableSectionContext as coreMakeExpandableSectionContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable ExpandableSectionContext.
 */
export const makeExpandableSectionContext = (
  props: Parameters<typeof coreMakeExpandableSectionContext>[0]
): LocationContext<ExpandableSectionContext> =>
  makeLocationContext<ExpandableSectionContext>(coreMakeExpandableSectionContext(props));
