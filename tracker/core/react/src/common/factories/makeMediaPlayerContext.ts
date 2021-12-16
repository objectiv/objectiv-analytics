/*
 * Copyright 2021 Objectiv B.V.
 */

import { MediaPlayerContext } from '@objectiv/schema';
import { makeMediaPlayerContext as coreMakeMediaPlayerContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable MediaPlayerContext.
 */
export const makeMediaPlayerContext = (
  props: Parameters<typeof coreMakeMediaPlayerContext>[0]
): LocationContext<MediaPlayerContext> => makeLocationContext<MediaPlayerContext>(coreMakeMediaPlayerContext(props));
