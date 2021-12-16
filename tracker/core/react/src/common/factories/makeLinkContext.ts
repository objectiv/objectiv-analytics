/*
 * Copyright 2021 Objectiv B.V.
 */

import { LinkContext } from '@objectiv/schema';
import { makeLinkContext as coreMakeLinkContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable LinkContext.
 */
export const makeLinkContext = (props: Parameters<typeof coreMakeLinkContext>[0]): LocationContext<LinkContext> =>
  makeLocationContext<LinkContext>(coreMakeLinkContext(props));
