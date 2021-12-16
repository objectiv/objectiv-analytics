/*
 * Copyright 2021 Objectiv B.V.
 */

import { SectionContext } from '@objectiv/schema';
import { makeSectionContext as coreMakeSectionContext } from '@objectiv/tracker-core';
import { LocationContext } from '../../types';
import { makeLocationContext } from './makeLocationContext';

/**
 * A utility to factor a new uniquely identifiable OverlayContext.
 */
export const makeSectionContext = (
  props: Parameters<typeof coreMakeSectionContext>[0]
): LocationContext<SectionContext> => makeLocationContext<SectionContext>(coreMakeSectionContext(props));
